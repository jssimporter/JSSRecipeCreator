JSSRecipeCreator (Ballin' Dubstep)
=================

This brief script allows one to rapidly make JSS recipes based on a set of template files. The recipes generated have (mostly) duplicated INPUT variables and JSSImporter arguments to further facilitate overriding the recipes. Since every organization structures their JSS differently, this allows a fair amount of sharing of recipes without needing to fork/copy/edit.

It has python-jss as a dependency, although if you're worried about making JSS recipes, you probably already have this. If not, grab it *with* the JSSImporter [here](https://www.github.com/sheagcraig/JSSImporter), and make sure it's set up. It is used to grab existing category and computer group information.

You will need some template files to make this work:
- RecipeTemplate: (Optional) Allows you to specify values that are common to all of your recipes. JSSRecipeCreator will search the current directory for a file named RecipeTemplate.xml (which can be configured in the globals). If it is present, it will be used. If there is no RecipeTemplate.xml, JSSRecipeCreator will create a blank recipe XML structure to fill for you. For more info, see the Recipe Template section below. You can also run JSSRecipeCreator with the ```-s``` flag to force creating a recipe on the fly, or the ```-r``` option to specify a different recipe template than the default.
- PolicyTemplate: This is the PolicyTemplate file you use with your JSSImporter recipes. The file doesn't actually need to be present, but if you copy it to the directory JSSRecipeCreator is running from, it will magically appear in the menu as an option, rather than having to key it in. Defaults to "PolicyTemplate.xml" (but you can change it in the globals section at the top of JSSRecipeCreator).
- SmartGroupTemplates: For each unique smart group you intend on using, you will need a SmartGroupTemplate (see the JSSImporter documentation for the structure of these). Again, it doesn't have to be present, but having it in the current working directory will allow default-discovery and speed up your process. The globals section specifies 'SmartGroupTemplate.xml' as the default choice, which can of course be changed to suit your needs.


Usage
=================
Run the script and provide the path to a valid *pkg* recipe you want to use as a parent as an argument:
```
$ ./JSSRecipeCreator.py ~/Library/Autopkg/RecipeRepos/com.github.autopkg.sheagcraig-recipes/Greenfoot/Greenfoot.pkg.recipe
```

Then follow the prompts. For each prompt, you can type a number to select from a list, enter a new value, or simply hit enter to accept the default value (if there is one). If you don't care about a particular value, like Self Service Icon, just don't provide a value, or leave it out of your recipe template file and it won't get added in.

- Recipe Filename: What you want your recipe's filename to be. It will take the parent recipe's filename and swap 'jss' for 'pkg' by default. Sometimes you may be basing your recipe off of someone else's, so you'll want to change the name to match your organization's naming policy.
- Recipe Identifier: Defaults to your parent recipe's identifier, with 'pkg' changed to 'jss'. Again, if you're basing off of someone else's recipe. you may want to change this.
- NAME: The required input to JSSImporter representing your product's name. Used all over the place!
- Policy Template: The filename of a JSSImporter policy template file. You should have a copy of this in your "build" directory.
- Package Category: The category to use for your recipe's Package. See Recipe Template section below.
- Policy Category: The category to use for your recipe's Policy. See Recipe Template section below.
- Scope: A submenu that walks you through adding values for any groups you want to scope. Scoping groups are *only* added to the JSSImporter processor arguments. See the Recipe Template section below.
- Self Service Icon: The filename for an icon file to be used in Self Service. JSSRecipeCreator will default to using the ```name``` of your product with a '.png' extension. Make sure this file is in your recipe directory before running!
- Self Service Description: The description used for Self Service policies.

Acute users will notice that there is no prompt for minimum_version. JSSRecipeCreator just pulls it from the parent recipe. Usually JSS recipes don't include a lot of other, newer AutoPkg processors or features, so this shouldn't make or break your recipe. It also handles ParentRecipe.


Advanced Options
=================
- ```-r / --recipe_template RECIPE_TEMPLATE``` allows you to specify an alternate recipe template file (default behavior is to use the one in the current working directory specified in the global ```DEFAULT_RECIPE_TEMPLATE```, which is provided as ```RecipeTemplate.xml``` May not be used with ```-s```.
- ```-s / ---from_scratch``` Do not use a recipe template. Creates a recipe file from scratch. May not be used with ```-r```.
- ```-a / --auto``` Speed up recipe creation even more! Automatically chooses default values whenever possible, only prompting you when there isn't one.


Recipe Template
=================
You will need a recipe template file for the JSSRecipeCreator to base its recipes from. If you have a working JSS recipe and workflow, you can start from it.

Except for scoping groups (the ```groups``` argument) and recipe values (like Identifier or MinimumVersion), JSSRecipeCreator adds all values to the INPUT section of a recipe, and your JSSImporter arguments should reference those INPUT variable names appropriately (see the provided RecipeTemplate.xml for an example. The specific INPUT variables managed (and thus they should be included in your template) are: 
- ```Comment``` (Extra comments you want to add, like author name. Can be set with the global RECIPE_COMMENT)
- ```Description```
- ```Identifier```
- ```CATEGORY``` (Package Category)
- ```DESCRIPTION``` (Self Service Description)
- ```ICON``` (Self Service Icon)
- ```NAME``` (Product name)
- ```POLICY_CATEGORY```
- ```POLICY_TEMPLATE```
- ```MinimumVersion```
- ```ParentRecipe```

Plus, you should have an element started for the JSSImporter processor.

I always use "Testing" for my self service policies, so I have added that value to my ```POLICY_CATEGORY``` in the template. JSSRecipeCreator will see that value and use it as a default. All of the above values work in the same way.


Advanced Recipe Creation
=================
What do you do if you have a more annoying recipe? One that involves extension attributes, scripts, or perhaps a pkg_id?

At this point, get as far as you can with the automated creation and then hand-edit! Or add in handling to this project and send me a pull-request. I would say that *most* of my recipes can be processed with JSSRecipeCreator, and those few that are problems often require iterating through several test versions anyway.

Enjoy!

Ballin' Dubstep?
=================
GitHub offers a project name if you don't want to come up with one. For this, it suggested 'ballin-dubstep', which is a pretty sweet name. Just not very descriptive of what this does.
