import pytest
from pathlib import Path
from app.recipe import Recipe

SAMPLE_RECIPES_FOLDER_PATH = Path(__file__).resolve().parent / 'sample_recipes'
ALL_RECIPE_PATHS = [p for p in SAMPLE_RECIPES_FOLDER_PATH.iterdir()]
OK_RECIPES = [p for p in ALL_RECIPE_PATHS if '_ok.txt' in p.name]
ERROR_RECIPES = [p for p in ALL_RECIPE_PATHS if '_error.txt' in p.name]
SAMPLE_RECIPE = Recipe(SAMPLE_RECIPES_FOLDER_PATH / 'sample_recipe_ok.txt')

class TestFileParsing:

    def test_should_parse_ok_recipes_without_error(self):
        for path in OK_RECIPES:
            recipe = Recipe(path)

    def test_should_throw_error_on_every_malformed_recipe(self):
        for path in ERROR_RECIPES:
            with pytest.raises(TypeError) as pytest_wrapped_e:
                recipe = Recipe(path)

class TestUnitConversion:

    def test_should_convert_cups_to_dl_correctly_1(self):
        iis = SAMPLE_RECIPE.ingredient_instructions['CAKE']
        wheat_flour = [x for x in iis if x.ingredient == 'wheat flour'][0]
        assert wheat_flour.amount == 4.731762500031148
        assert wheat_flour.unit == 'dl'

    def test_should_convert_cups_to_dl_correctly_2(self):
        iis = SAMPLE_RECIPE.ingredient_instructions['CAKE']
        wheat_flour = [x for x in iis if x.ingredient == 'coco powder'][0]
        assert wheat_flour.amount == 1.7744109375116803
        assert wheat_flour.unit == 'dl'

    def test_should_convert_lbs_to_g_correctly(self):
        path = SAMPLE_RECIPES_FOLDER_PATH / 'chicken_marinade_1_ok.txt'
        r = Recipe(path)
        iis = r.ingredient_instructions['main']
        chicken = [x for x in iis if x.ingredient == 'chicken'][0]
        assert chicken.amount == 907.184
        assert chicken.unit == 'g'
