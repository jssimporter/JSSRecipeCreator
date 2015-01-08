### 0.0.4 (UNRELEASED) Michaelangelo is a Party Dude

CHANGES:

- Apparently I named the script file JSSRecipeGenerator.py, despite *every* other instance. Everything has been normalized to JSSRecipeCreator. Sorry for the confusion!

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
