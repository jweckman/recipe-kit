from bs4 import BeautifulSoup
import requests
import lxml
from pathlib import Path
import re
from app.calc import spelling as unit_spelling
from app.recipe import Recipe, IngredientInstruction

class UrlParser:

    def __init__(self, url=None):
        self.url = url
        self.supported_sites = {
                'allrecipes.com': self.allrecipes
        }
        if not self.url:
            self.html = None
            self.soup = None
        else:
            self.get_soup()

    def extract_recipe(self, url):
        self.url = url
        self.get_soup()
        match = False
        for site, site_function in self.supported_sites.items():
            if site in self.url.lower():
                match=True
                recipe = Recipe(**site_function())
                return recipe 
        if not match:
            print(f"URL {self.url} not supported, consider writing your own functions under the UrlParser class")

    def get_soup(self):
        self.html = requests.get(self.url).text
        self.soup = BeautifulSoup(self.html, 'lxml')

    def first_non_num_index(self, s:str) -> int:
        numbers = '0123456789½¼⅛¾⅓'
        for i,c in enumerate(s):
            if c.isspace() or c in numbers:
                continue
            return i

    def allrecipes_ingredients(self):
        # Ingredients to IngredientInstruction named tuple logic
        ingredients = self.soup.find_all(class_='ingredients-item-name')
        number_regex = '[0-9½¼⅛¾⅓]'
        unicode_fraction_conversion = {'½': .5,'¼': .25,'⅛': .125,'¾': .75, '⅓': 0.3333333333333333}
        ingredient_instructions = [] 
        for ig in ingredients:
            # Amount of ingredients
            ig = ig.text.strip()
            # Remove parentheses and their content
            ig = re.sub(r'\([^)]*\)', '', ig)
            fnni = self.first_non_num_index(ig)
            numbers = re.findall(number_regex,ig[:fnni])
            if numbers:
                ig = ig[fnni:]

                amount = 0 
                unicode_fraction_amount = 0
                if numbers[-1] in unicode_fraction_conversion:
                    f = numbers.pop(-1)
                    unicode_fraction_amount = unicode_fraction_conversion[f] 
                if numbers:
                    amount = int(''.join(numbers))
                amount = amount + unicode_fraction_amount
            else:
                amount = 0 
            # Try to find unit
            unit = None
            for spelling in unit_spelling.keys():
                if spelling in ig.lower():
                    unit = unit_spelling[spelling]
                    insensitive_regex = re.compile(re.escape(spelling), re.IGNORECASE)
                    ig = insensitive_regex.sub('', ig) 
                    if ig[:2] == 's ':
                        ig = ig[2:]
            ig = ig.strip()
            if amount == 0:
                ingredient_instructions.append(IngredientInstruction(1,'pcs',ig))
            elif unit == None:
                if amount == 0:
                    amount = 1
                ingredient_instructions.append(IngredientInstruction(amount,'pcs',ig))
            else:
                ingredient_instructions.append(IngredientInstruction(amount,unit,ig))

        return ingredient_instructions

    def allrecipes_instructions(self):
        html_class="subcontainer instructions-section-item"
        #html_class="instructions-section"
        containers = self.soup.find_all(class_ = html_class)
        return [c.find('p').getText() for c in containers]
        for c in containers:
            c.find('p').getText()

    def allrecipes_meta(self):
        mi = "recipe-meta-item"
        raw = self.soup.find_all(class_ = mi)
        relevant_meta = []
        for l in raw:
            for child in l.children:
                if child.string.isspace():
                    continue
                else:
                    relevant_meta.append(child.string)
        recipe_name_class = "headline heading-content"
        raw_name = self.soup.find_all(class_ = recipe_name_class)[0]
        o = {'servings': None, 'name': raw_name.string}

        for i,rm in enumerate(relevant_meta):
            if rm.strip() == 'Servings:':
                o['servings'] = int(relevant_meta[i+1])
        return o

    def allrecipes(self):
        iis = self.allrecipes_ingredients()
        instructions = self.allrecipes_instructions()
        meta = self.allrecipes_meta()
        output = {'original_sources': [self.url], 'ingredient_instructions': {'main': iis}, 'instructions': {'main': instructions}, **meta}

        return output 

if __name__ == '__main__':
    url = 'https://www.allrecipes.com/recipe/279934/air-fryer-apricot-glazed-chicken-breasts/'
    up = UrlParser(url)
    up.extract_recipe()
