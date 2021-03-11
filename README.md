# recipe-kit
(WIP)
Cooking kit for standardizing recipes found online and converting them to an international standard format. Supports reading from certain websites and reading from/to the standard .txt based format.

## Benefits
* unified way to store recipes
* built-in scaling calculations
* enables any UI to be built on top
* small form-factor that can be stored anywhere

## Features
* standard .txt format for documenting recipes.
* calculator for easily scaling recipes according to user needs
* URL parser for popular recipe sites, as well as fallback option for general recipe site
* Simple terminal UI for navigating recipes in a folder structure

## Standard format for storing recipes
Example of suggested standard format in sample recipe .txt file.

The standard includes:
* recipe version, to give an idea of how many iterations have been made before arriving at end result. Suggested to start from 1.0 and adding 0.1 for each version.
* ingredient list with amounts specified in litres, grams, tablespoons, and teaspoons _per person_
* step by step guide for execution that may include images
* tags for categorizing and searching
