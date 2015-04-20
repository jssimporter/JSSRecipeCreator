# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased][unreleased]

## [1.0.0] - 2015-04-20 Bodacious
### CHANGED
- You can now specify any number of parent recipes on the commandline, and JSSRecipCreator will take you through the generation process for each one.
- Reformatted CHANGELOG...
- Style and lint updates for code beauty.
- Uses more specific exception subclasses.
- Added optionality to menus. For example, you can now specify that you don't want a policy template by selecting the ```0: <None> option.
- Detects parent recipes that will require an empty <version> tag (uses PlistReader) and puts one in.
- Standardized and reformatted menus and lists.

### FIXED
- Solves unhandled exception when an invalid entry is made during auto mode.
- Handles parent recipes and recipe templates that don't have the full range of expected keys.

## [0.1.0] - 2015-01-14 Michaelangelo is a Party Dude
### CHANGED
- Apparently I named the script file JSSRecipeGenerator.py, despite *every* other instance. Everything has been normalized to JSSRecipeCreator. Sorry for the confusion!
- Added recipe comments to help spread the word.
- Massively refactored for better design.
- Added preference file and handling system for default values. (See README).
- A RecipeTemplate is no longer required (although still recommended!). It can create jss.recipes from scratch.
	- You can also create a blank AutoPkg recipe if you use the code as a module.
- Added -a/--auto argument. Uses all default settings without prompting, and only prompts for those which don't have a default.
- You may now add as many scoping groups as you want. Please see the README.
- User choices are now validated.
- RecipeTemplates now no longer use "replacement variables".
	- Thus, all replacement variables have been removed from the provided template.
- Included a copy of the standard JSSImporter SmartGroup and Policy templates, as well as updated documentation to indicate the advantage of them being present in the CWD.

### FIXED
- Category questions would fail if given a blank category name (trying to coerce None to a string type). This has been corrected (#4)

## [0.0.3] - 2014-12-19 Linty
### CHANGED

- Now does a quick "lint" check of XML with ```plutil -lint``` after generation.
- readline support added so you can use those sweet terminal hotkeys.

## [0.0.2] - 2014-12-18 Stomper
### CHANGED
- Now uses AutoPkg configuration file. Hopefully you already have this configured for JSSImporter use!
- Optional argument -r/--recipe_template allows you to use a different recipe template file.

### FIXED
- Now prompts for a NAME if one doesn't exist. It does not, sadly, suggest "ballin' dubstep" as a potential name. 

## [0.0.1] - 2014-12-17 Ballin' Dubstep

Initial Release
