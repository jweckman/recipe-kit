from app.recipe import Recipe
from pathlib import Path

if __name__ == '__main__':
    sample = Path().cwd() / 'sample_recipe.txt'
    r = Recipe(sample)
    r.convert()
    print(str(r))

