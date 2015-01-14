### 0.1.0 (January 14, 2015) Michaelangelo is a Party Dude

CHANGES:

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

FIXES:

- Category questions would fail if given a blank category name (trying to coerce None to a string type). This has been corrected (#4)

### 0.0.3 (December 19, 2014) Linty

CHANGES:

- Now does a quick "lint" check of XML with ```plutil -lint``` after generation.
- readline support added so you can use those sweet terminal hotkeys.

### 0.0.2 (December 18, 2014) Stomper

CHANGES:
- Now uses AutoPkg configuration file. Hopefully you already have this configured for JSSImporter use!
- Optional argument -r/--recipe_template allows you to use a different recipe template file.

FIXES:
- Now prompts for a NAME if one doesn't exist. It does not, sadly, suggest "ballin' dubstep" as a potential name. 

### 0.0.1 (December 17, 2014) Ballin' Dubstep

Initial Release
