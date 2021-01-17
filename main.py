from pathlib import Path
import sys
from app.recipe import Recipe
from app.url_parser import UrlParser

def read_file():
    print(sys.argv)
    if len(sys.argv) == 1:
        f = Path().cwd() / 'sample_recipe.txt'
        r = Recipe(f)
        print('This is a sample recipe. Please specify file path as first argument and serving amount as second argument')
    elif len(sys.argv) == 2:
        r = Recipe(sys.argv[1])
        print('TIP: To change sercving amount, add it as the second argument')
    elif len(sys.argv) == 3:
        print('RAN')
        r = Recipe(sys.argv[1])
        r.rescale(sys.argv[2])
    else:
        print('Too many arguments specified')
        print('Please specify file path as first argument and serving count as second argument')
    r.pretty_print()

def read_url():
    url = 'https://www.allrecipes.com/recipe/279934/air-fryer-apricot-glazed-chicken-breasts/'
    url = 'https://www.allrecipes.com/recipe/20185/virginas-tuna-salad/'
    url = 'https://www.allrecipes.com/recipe/7934/blueberry-cheesecake/'
    url = 'https://www.allrecipes.com/recipe/15246/yummy-fruit-pizza/'
    url = 'https://www.allrecipes.com/recipe/218586/walnut-banana-bread-pudding/'
    up = UrlParser()
    #recipe2 = Recipe(path = Path().cwd() / 'sample_recipe.txt')
    #recipe2.pretty_print()
    recipe = up.extract_recipe(url)
    recipe.pretty_print()
    recipe.write_txt()

if __name__ == '__main__':
    read_url()
    #read_file()

