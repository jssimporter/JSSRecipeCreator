JSSRecipeCreator (Ballin' Dubstep)
=================

This brief script allows one to rapidly make JSS recipes based on a set of template files.

It has python-jss as a dependency, although if you're worried about making JSS recipes, you probably already have this. If not, grab it *with* the JSSImporter [here](https://www.github.com/sheagcraig/JSSImporter), and make sure it's set up. It is used to grab existing category information.

You will need some template files to make this work:
- RecipeTemplate: This is the template file which the gets filled with information you provide.
- PolicyTemplate: This is the PolicyTemplate file you use with your JSSImporter recipes. The file doesn't actually need to be present, but if you copy them to the directory JSSRecipeCreator is running from, they will magically appear in the menu as options, rather than having to key them in. Defaults to "PolicyTemplate.xml" (but you can change it in the globals section at the top of JSSRecipeCreator).
- GroupTemplate: As per above. At this time, it only does a single group, so if you're scoping a ton of groups in your policies, send me a GitHub issue that you would like to see it added.

Run the script and provide the path to a valid *pkg* recipe as its only argument:
```
$ ./JSSRecipeCreator.py ~/Library/Autopkg/RecipeRepos/com.github.autopkg.sheagcraig-recipes/Greenfoot/Greenfoot.pkg.recipe
```

Then follow the prompts. For each prompt, you can type a number to select from a list, enter a new value, or simply hit enter to accept the default value (if there is one). If you don't care about a particular value, like Self Service Icon, just don't provide a value, or leave it out of your recipe template file and it won't get subbed in.

- Recipe Filename: What you want your recipe's filename to be. It will take the parent recipe's filename and swap 'jss' for 'pkg' by default. Sometimes you may be basing your recipe off of someone else's, so you'll want to change the name to match your organization's naming policy.
- Recipe Identifier: Defaults to your parent recipe's identifier, with 'pkg' changed to 'jss'. Again, if you're basing off of someone else's recipe. you may want to change this.
- Package Category: The category to use for your recipe's Package. See Recipe Template section below.
- Policy Category: The category to use for your recipe's Policy. See Recipe Template section below.
- Policy Template: The filename of a JSSImporter policy template file. You should have a copy of this in your "build" directory.
- Group Template: The filename of a JSSImporter group template file. You should have a copy of this in your "build" directory.
- Self Service Icon: The filename for an icon file to be used in Self Service. JSSRecipeCreator will default to using the ```name``` of your product with a '.png' extension. Make sure this file is in your recipe directory before running!
- Product Description: This is for any description you might want to appear in your self service policy.

Acute users will notice that there is no prompt for minimum_version. JSSRecipeCreator just pulls it from the parent recipe. Usually JSS recipes don't include a lot of other, newer AutoPkg processors or features, so this shouldn't make or break your recipe.


Recipe Template
=================
You will need a recipe template file for the JSSRecipeCreator to base its recipes from. If you have a working JSS recipe, you can swap in the following replacement variables to allow the JSSRecipeCreator to fill in values:
- ```%RECIPE_IDENTIFIER%```
- ```%PARENT_RECIPE%```
- ```%PRODUCT_NAME%```
- ```%RECIPE_DESCRIPTION%```
- ```%RECIPE_PRODUCT_DESCRIPTION%```
- ```%MINIMUM_VERSION%```
- ```%RECIPE_PKG_CATEGORY%```
- ```%RECIPE_POLICY_CATEGORY%```
- ```%RECIPE_POLICY_TEMPLATE%```
- ```%RECIPE_GROUP_TEMPLATE%```
- ```%RECIPE_ICON%```

I always use the category "Testing" for my policy categories, so if you *do not* specify a replacement variable in a category field of your recipe template, but instead specify a category, the JSSRecipeCreator will just skip prompting you for that value, speeding things up a little bit.

As mentioned earlier, if you don't want a substitution to occur, you can avoid putting one of the above replacement variables in. Also, if you look at the included ```RecipeTemplate.xml```, you can see that it is possible to combine JSSRecipeCreator substitutions with substitutions intended for later processing via JSSImporter and AutoPkg.

Advanced Recipe Creation
=================
What do you do if you have a more annoying recipe? One that involves extension attributes, scripts, or perhaps a pkg_id?

At this point, get as far as you can with the automated creation and then hand-edit! Or add in handling to this project and send me a pull-request. I would say that *most* of my recipes can be processed with JSSRecipeCreator, and those few that are problems often require iterating through several test versions anyway.

Enjoy!

Ballin' Dubstep?
=================
GitHub offers a project name if you don't want to come up with one. For this, it suggested 'ballin-dubstep', which is a pretty sweet name. Just not very descriptive of what this does.
