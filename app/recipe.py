from pathlib import Path
from collections import namedtuple
import textwrap
import sys
if __name__ != '__main__':
    from app.calc import convert_value
else:
    from calc import convert_value

IngredientInstruction = namedtuple('IngredientInstruction', 'ingredient, amount, unit')

class Recipe:
    '''Class for reading in, storing, and printing recipes to the terminal'''
    def __init__(self, path, default_conversion='metric'):
        self.path = path
        self.default_conversion = default_conversion
        self.recipe_raw = self._read_file(path) 
        self.name = None
        self.authors = []
        self.original_sources = []
        self.version = '1.0'
        self.tags = []
        self.servings = 1
        self.equipment=[]
        self.ingredient_instructions = dict()
        self.instructions = dict() 
        self.original_sources= []
        self._process_raw()
        self.convert()
        
    def _read_file(self, path):
        '''Read raw recipe .txt as list of strings'''
        with open(path, 'r') as fp:
            return fp.read().splitlines()

    def _get_raw_sections(self):
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

    def _process_raw(self):
        ''' Find raw .txt data and populate instance attributes'''
        # Get the sections from the raw .txt document
        ingredients_start, instructions_start, subsections = self._get_raw_sections()

        # Get initial attributes
        for l in self.recipe_raw[:ingredients_start-1]:
            ll = l.lower()
            if ll[:5] == 'name=':
                self.name = l[5:]
            if ll[:8] == 'authors=':
                self.authors = l[8:].split(',')
            if ll[:17] == 'original sources=':
                self.original_sources = l[17:].split(',')
            if ll[:8] == 'version=':
                self.version = l[8:]
            if ll[:5] == 'tags=':
                self.tags = l[5:].split(',')
            if ll[:9] == 'servings=':
                self.servings = int(l[9:])
            if ll[:10] == 'equipment=':
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
                    self.ingredient_instructions[current_subsection].append(IngredientInstruction(*l.split(','), 'pcs'))

        # Get instructions for making the recipe and add as list of string under lables as keys
        current_subsection = None

        for row in self.recipe_raw[instructions_start:]:
            if row.strip().isupper():
               current_subsection = row.strip().lower() 
            if '.' not in row:
                continue
            if row.split('.')[0].strip().isnumeric():
                row_numbers, rest = row.split('.', 1)
                row_numbers = row_numbers + '.\t'
                row = row_numbers + rest
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
                o[subsection].append(IngredientInstruction(ii[0],new_amount,new_unit))
        self.ingredient_instructions = o

    def rescale(self, new_servings):
        '''Rescale amount of portions'''
        new_servings = float(new_servings)
        o = {k: [] for k in self.ingredient_instructions.keys()}
        for subsection, iis in self.ingredient_instructions.items():
            for ii in iis:
                single_serving_amount = ii.amount / self.servings
                new_amount = single_serving_amount * new_servings 
                o[subsection].append(IngredientInstruction(ii.ingredient,new_amount,ii.unit))
        self.servings = new_servings
        self.ingredient_instructions = o

    def _print_ingredient_instruction(self,ii,longest_ingredient_length):
        '''Helper function for pretty_print'''
        space_count = longest_ingredient_length - len(ii.ingredient)
        spaces = ' ' * space_count + ' '
        if ii.amount.is_integer():
            print(f"{ii.ingredient}{spaces}{int(ii.amount)}\t{ii.unit}")
        else:
            print(f"{ii.ingredient}{spaces}{round(ii.amount,1)}\t{ii.unit}")

    def pretty_print(self):
        '''Pretty prints the recipe in the terminal'''
        if not self.name or not self.ingredient_instructions:
            print('Read file does not have a name and ingredient instruction, aborting')
            sys.exit()
        print(f"---------------{self.name}---------------")
        print(f"version: {self.version}")
        print(f"authors: {', '.join(self.authors)}")
        print(f"original sources: {', '.join(self.original_sources)}")
        print(f"tags: {', '.join(self.tags)}")

        # Ingredients
        print("\n---------------INGREDIENTS---------------\n")
        for ic, iis in self.ingredient_instructions.items():
            if ic != 'main':
                print(f"\n----------{ic.upper()}----------\n")
            longest_ingredient_length = len(max(iis, key=lambda k: len(k.ingredient)).ingredient) 
            for ii in iis:
                self._print_ingredient_instruction(ii, longest_ingredient_length)

        # Instructions
        print('\n---------------INSTRUCTIONS---------------\n')
        for category, instructions in self.instructions.items():
            if category != 'main':
                print('\n' + category.upper() + '\n')
            for row in instructions:
                numlen = len(row.split('.')[0])
                for i,l in enumerate(textwrap.wrap(row, 100)):
                    if i == 0:
                        print(l)
                    else:
                        spaces = ' ' * numlen
                        print('\t' + spaces + l)
        
    def __str__(self):
        return f"{self.name}\n{self.authors}\n{self.version}\n{self.tags}\n{self.servings},\n{self.ingredient_instructions}"

if __name__ == '__main__':
    sample = Path().cwd().parent / 'sample_recipe2.txt'
    rp = Recipe(sample)
    rp.convert()
    rp.rescale(10)
    rp.pretty_print()
