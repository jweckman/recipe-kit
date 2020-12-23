from bs4 import BeautifulSoup
import requests
import lxml
from pathlib import Path
import re
from app.calc import spelling as unit_spelling

class UrlParser:

    def __init__(self, url):
        self.url = url
        self.html = requests.get(url).text
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.supported_sites = {
                'allrecipes.com': self.allrecipes
        }

    def extract_recipe(self):
        for site, site_function in self.supported_sites.items():
            if site in self.url.lower():
                site_function()

    def allrecipes(self):
        # Ingredients to IngredientInstruction named tuple logic
        ingredients = self.soup.find_all(class_='ingredients-item-name')
        number_regex = '[0-9½¼⅛¾]'
        unicode_fraction_conversion = {'½': '.5','¼': '.25','⅛': '.125','¾': '.75'}
        for ig in ingredients:
            # Amount of ingredients
            ig = ig.text.strip()
            # Remove parentheses and their content
            ig = re.sub(r'\([^)]*\)', '', ig)
            print(ig)
            numbers = re.findall(number_regex,ig[:4])
            amount = None
            for i,item in enumerate(numbers.copy()):
                ig = ig.replace(item, '')
                if item in unicode_fraction_conversion.keys():
                    numbers[i] = float(numbers[i].replace(item,unicode_fraction_conversion[item]))
                    amount = ''.join(numbers[:-1]) + numbers[-1]
            if not amount and len(numbers) > 0:
                amount = ''.join(numbers)
            # Try to find unit
            unit = None
            for spelling in unit_spelling.keys():
                if spelling in ig.lower():
                    unit = unit_spelling[spelling]
                    insensitive_regex = re.compile(re.escape(spelling), re.IGNORECASE)
                    ig = insensitive_regex.sub('', ig) 
            print(unit)
            print(ig)




if __name__ == '__main__':
    url = 'https://www.allrecipes.com/recipe/279934/air-fryer-apricot-glazed-chicken-breasts/'
    up = UrlParser(url)
    up.extract_recipe()
