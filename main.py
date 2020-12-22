from app.recipe import Recipe
from pathlib import Path
import sys

if __name__ == '__main__':
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
