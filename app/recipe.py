from pathlib import Path
from collections import namedtuple
import textwrap
import sys
from copy import copy
if __name__ != '__main__':
    from app.calc import convert_value
else:
    from calc import convert_value

IngredientInstruction = namedtuple('IngredientInstruction', 'amount, unit, ingredient')

class Recipe:
    '''Class for reading in, storing, and printing recipes to the terminal'''
    def __init__(self, 
                    path=None,
                    default_conversion = 'metric', 
                    recipe_raw = None, 
                    name = None,
                    authors = [],
                    original_sources = [],
                    version = '1.0',
                    tags = [],
                    servings = 1,
                    equipment=[],
                    ingredient_instructions = dict(),
                    instructions = dict(),
                    ):
        self.default_conversion = default_conversion
        self.name = name 
        self.authors = authors 
        self.original_sources = original_sources 
        self.version = version 
        self.tags = tags 
        self.servings = servings 
        self.equipment = equipment
        self.ingredient_instructions = ingredient_instructions 
        self.instructions = instructions 
        self.path = path
        if path:
            self.recipe_raw = self.read_txt(path) 
            self._process_txt()
        self.convert()
        self.change_ingredient_illegal_chars()
        
    def change_ingredient_illegal_chars(self):
        cp = copy(self.ingredient_instructions)
        for category,iis in cp.items():
            for i, ii in enumerate(iis):
                changed = ii.ingredient.replace(',', ' -')
                self.ingredient_instructions[category][i] = IngredientInstruction(ii.amount, ii.unit, changed) 

    def read_txt(self, path):
        '''Read raw recipe .txt as list of strings'''
        with open(path, 'r') as fp:
            return fp.read().splitlines()

    def write_txt(self):
        # Make user specify a file path if still undefined
        if not self.path:
            while True:
                try:
                    new_path = Path(input("No file has been specified for this recipe yet. Please enter where you wish to save the file:\nE.g: /home/user/recipes/my_recipe.txt\n"))
                except:
                    print(f"Path {new_path} invalid, please add different path\n")
                    continue
                break
            self.path = new_path 
        
        # Gather data into a single list
        lines = []

        if not self.name or not self.ingredient_instructions:
            print('Recipe does not have a name and ingredient instruction, aborting')
            sys.exit()
        lines.append('name=' + self.name + '\n')
        lines.append('authors=' + ', '.join(self.authors) + '\n')
        lines.append('original_sources=' + ', '.join(self.original_sources) + '\n')
        lines.append('tags=' + ', '.join(self.tags) + '\n')
        lines.append('servings=' + str(self.servings) + '\n')
        lines.append('INGREDIENTS' + '\n')
        for ic, iis in self.ingredient_instructions.items():
            if ic != 'main':
                lines.append(f"{ic.upper()}\n")
            for ii in iis:
                lines.append(','.join([str(x) for x in ii]) + '\n')
        lines.append('INSTRUCTIONS' + '\n')
        for category, instructions in self.instructions.items():
            if category != 'main':
                lines.append(category.upper() + '\n')
            for i, row in enumerate(instructions):
                lines.append(f"{i+1}. {row}\n")

        # Write to file
        with open(self.path, 'w', encoding='utf-8') as fp:
            fp.writelines(lines)

    def get_txt_sections(self):
        ''' Find sections and their names in raw .txt'''
        ingredients_start = None
        instructions_start = None
        subsections = {'ingredients': dict(), 'instructions': dict()}
        current_section = 'start'
        for i,l in enumerate(self.recipe_raw):
            l = l.replace('\n', '')
            if l[:11] == 'INGREDIENTS':
               ingredients_start = i+1 
               current_section = 'ingredients'
            if l[:12] == 'INSTRUCTIONS':
                instructions_start = i+1
                current_section = 'instructions'
            if current_section == 'ingredients' and l.isupper():
                subsections['ingredients'][i] = l
            if current_section == 'instructions' and l.isupper():
                subsections['instructions'][i] = l
        return ingredients_start, instructions_start, subsections

    def _process_txt(self):
        ''' Find raw .txt data and populate instance attributes'''
        # Get the sections from the raw .txt document
        ingredients_start, instructions_start, subsections = self.get_txt_sections()

        # Get initial attributes
        for l in self.recipe_raw[:ingredients_start-1]:
            ll = l.lower()
            if ll[:5] == 'name=' and len(ll) > 5:
                self.name = l[5:]
            if ll[:8] == 'authors=' and len(ll) > 8:
                self.authors = l[8:].split(',')
            if ll[:17] == 'original sources=' and len(ll) > 17:
                self.original_sources = l[17:].split(',')
            if ll[:8] == 'version=' and len(ll) > 8:
                self.version = l[8:]
            if ll[:5] == 'tags=' and len(ll) > 5:
                self.tags = l[5:].split(',')
            if ll[:9] == 'servings=' and len(ll) > 9:
                self.servings = int(l[9:])
            if ll[:10] == 'equipment=' and len(ll) > 10:
                self.equipment = l[10:].split(',')
        
        # Get ingredient instructions as named tuples and add to dictionary with lables as keys
        current_subsection = None

        for i,l in enumerate(self.recipe_raw[ingredients_start:instructions_start]):
            i = i+ingredients_start
            if i in subsections['ingredients'].keys():
                current_subsection = subsections['ingredients'][i]
                continue

            if current_subsection not in self.ingredient_instructions and current_subsection:
                self.ingredient_instructions[current_subsection] = []
            if len(l) > 4  and ',' in l:
                if not current_subsection:
                    self.ingredient_instructions['main'] = []
                    current_subsection = 'main'
                if len(l.split(',')) == 3:
                    self.ingredient_instructions[current_subsection].append(IngredientInstruction(*l.split(',')))
                if len(l.split(',')) == 2:
                    short_amt, short_ingredient = l.split(',')
                    self.ingredient_instructions[current_subsection].append(IngredientInstruction(short_amt, 'pcs', short_ingredient))

        # Get instructions for making the recipe and add as list of string under lables as keys
        current_subsection = None

        for row in self.recipe_raw[instructions_start:]:
            if row.strip().isupper():
               current_subsection = row.strip().lower() 
            if '.' not in row:
                continue
            if row.split('.')[0].strip().isnumeric():
                row_numbers, rest = row.split('.', 1)
                row = rest.strip()
                if current_subsection:
                    if current_subsection not in self.instructions.keys():
                        self.instructions[current_subsection] = []
                    self.instructions[current_subsection].append(row)
                else:
                    self.instructions['main'] = []
                    current_subsection = 'main'
                    self.instructions['main'].append(row)

    def convert(self):
        '''Convert from imperial to metric units'''
        o = {k: [] for k in self.ingredient_instructions.keys()}
        for subsection, iis in self.ingredient_instructions.items():
            for ii in iis:
                new_amount, new_unit = convert_value(ii.amount, ii.unit)
                o[subsection].append(IngredientInstruction(new_amount,new_unit,ii.ingredient))
        self.ingredient_instructions = o

    def rescale(self, new_servings):
        '''Rescale amount of portions'''
        new_servings = float(new_servings)
        o = {k: [] for k in self.ingredient_instructions.keys()}
        for subsection, iis in self.ingredient_instructions.items():
            for ii in iis:
                single_serving_amount = ii.amount / self.servings
                new_amount = single_serving_amount * new_servings 
                o[subsection].append(IngredientInstruction(new_amount, ii.unit, ii.ingredient))
        self.servings = new_servings
        self.ingredient_instructions = o

    def _ingredient_pretty_print_space_string(self, s, longest_string_length):
        ''' Generates the needed amount of spaces to print nicely based on the longest string length)'''
        space_count = longest_string_length - len(str(s))
        return ' ' * space_count + ' '

    def _print_ingredient_instruction(self,ii,longest_ingredient_length, longest_amount_length):
        '''Helper function for pretty_print'''
        ingredient_spaces = self._ingredient_pretty_print_space_string(ii.ingredient, longest_ingredient_length)
        amount_spaces = self._ingredient_pretty_print_space_string(round(ii.amount,1), longest_amount_length)
        if isinstance(ii.amount, int):
            print(f"{ii.ingredient}{ingredient_spaces}{ii.amount}{amount_spaces + '  '}{ii.unit}")
        elif ii.amount.is_integer():
            print(f"{ii.ingredient}{ingredient_spaces}{int(ii.amount)}{amount_spaces + '  '}{ii.unit}")
        else:
            print(f"{ii.ingredient}{ingredient_spaces}{round(ii.amount,1)}{amount_spaces}{ii.unit}")

    def pretty_print(self):
        '''Pretty prints the recipe in the terminal'''
        if not self.name or not self.ingredient_instructions:
            print('Recipe does not have a name and ingredient instruction, aborting')
            sys.exit()
        print(f"---------------{self.name}---------------")
        print(f"version: {self.version}")
        print(f"authors: {', '.join(self.authors)}")
        print(f"original sources: {', '.join(self.original_sources)}")
        print(f"tags: {', '.join(self.tags)}")
        print(f"servings: {str(self.servings)}")

        # Ingredients
        print("\n---------------INGREDIENTS---------------\n")
        for ic, iis in self.ingredient_instructions.items():
            if ic != 'main':
                print(f"\n----------{ic.upper()}----------\n")
            longest_ingredient_length = len(str(max(iis, key=lambda k: len(str(k.ingredient))).ingredient))
            longest_amount_length = len(str(max(iis, key=lambda k: len(str(round(k.amount, 1)))).amount))
            for ii in iis:
                self._print_ingredient_instruction(ii, longest_ingredient_length, longest_amount_length)

        # Instructions
        print('\n---------------INSTRUCTIONS---------------\n')
        for category, instructions in self.instructions.items():
            if category != 'main':
                print('\n' + category.upper() + '\n')
            for i,row in enumerate(instructions):
                for j,l in enumerate(textwrap.wrap(row, 100)):
                    if j == 0:
                        print(f"{i+1}. {l}")
                    else:
                        print(l)
                print('\n')

    def __str__(self):
        return f"Name:{self.name}\nAuthors:{self.authors}\nVersion:{self.version}\nTags:{self.tags}\nServings:{self.servings},\nIngredient Instructions:{self.ingredient_instructions}"

if __name__ == '__main__':
    sample = Path().cwd().parent / 'sample_recipe2.txt'
    rp = Recipe(sample)
    rp.convert()
    rp.rescale(10)
    rp.pretty_print()
