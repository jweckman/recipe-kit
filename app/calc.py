import re
from fractions import Fraction
import sys
''' Calculations for converting between metric and imperial units '''


def second_level_keys(d):
    o = []
    for v in d.values():
        o = o + list(v.keys())
    return o

def string_to_number(s):
    try:
        return float(s)
    except:
        try:
            return float(Fraction(s))
        except:
            print(f"Could not turn {s} into a number, please correct your recipe")
            sys.exit()

def convert_value(val, val_unit: str):
    ''' Converts a given value from imperial to metric in the cooking context.
        Leaves value and unit unchanged if no conversion could be applied,
        printing that conversion was unsuccessful'''
    val_unit = str(val_unit)
    if val_unit == 'pcs':
        val = string_to_number(val)
        return val, val_unit
    val_unit = val_unit.lower()
    val_unit = re.sub(r'\s+','',val_unit)
    if val_unit[-1] == 's' and val_unit != 'ts':
        val_unit = val_unit[:-1]
    if val_unit in spelling.keys():
        val_unit = spelling[val_unit]
    if val_unit in ['pcs','tbsp','ts','pinch']:
        val = string_to_number(val)
        return val, val_unit
    if val_unit in mass_units:
        for v in mass.values():
            if val_unit in v.keys():
                new_val = string_to_number(val)
                new_val = new_val /  v[val_unit]  
                return new_val, 'g'
    if val_unit in vol_units:
        for v in vol.values():
            if val_unit in v.keys():
                new_val = string_to_number(val)
                new_val = new_val /  v[val_unit]  
                return new_val, 'dl'
    print(f"Could not convert {val} with unit {val_unit}, left unchanged")

    return val, val_unit 

vol = {
        "imp":{
            "floz": 3.3814038638, 
            "cup": 0.42267548297
        },
        "metric":{
            "dl": 1,
            "ml": 100,
            "l": 0.1 
        },
        "general":{
            "tbsp": 6.66666666666,
            "ts": 20
        }
}
mass = {
        "imp":{
            "oz":28.3495,
        },
        "metric":{
            "g": 1,
            "kg": 0.001
        },
        "general":{
            "pinch": 0.355625 
        }
}
 
spelling = {
        "fluid ounce": "floz",
        "fl.oz" : "floz",
        "deciliter": "dl",
        "decilitre": "dl",
        "millilitre": "ml",
        "milliliter": "ml",
        "cups": "cup",
        "cup": "cup",
        "coups": "cup",
        "coup": "cup",
        "liter": "l",
        "litre": "l",
        "tablespoon": "tbsp",
        "teaspoon": "ts",
        "ounce": "oz",
        "gram": "g",
        "kilogram": "kg",
        "pieces": "pcs",
        "units": "pcs",
        "stück": "pcs",
        "kpl": "pcs",
        "stycken": "pcs",
        "pinches": "pinch",
        "pinch": "pinch"
}

mass_units = second_level_keys(mass)
vol_units = second_level_keys(vol)
