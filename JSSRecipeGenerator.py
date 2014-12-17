#!/usr/bin/env python
"""JSSRecipeCreator.py

Quickly create JSS recipes from a template.

Copyright (C) 2014 Shea G Craig <shea.craig@da.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os.path
import sys
from xml.etree import ElementTree

from Foundation import (NSData,
                        NSPropertyListSerialization,
                        NSPropertyListMutableContainers)
import jss


DEFAULT_RECIPE_TEMPLATE = 'RecipeTemplate.xml'
DEFAULT_POLICY_TEMPLATE = 'PolicyTemplate.xml'
DEFAULT_GROUP_TEMPLATE = 'SmartGroupTemplate.xml'


class JSSRecipeCreator(object):
    """Quickly build a jss recipe from a parent recipe."""
    def __init__(self, parent_recipe_path):
        """Given a path to a parent recipe, pull all needed information.

        parent_recipe_path should be a path to a *pkg* recipe.

        """
        # Parse our parent recipe.
        parent_recipe_path = os.path.expanduser(parent_recipe_path)
        parent_recipe_name = os.path.basename(parent_recipe_path)
        if not 'PKG' in parent_recipe_name.upper():
            raise Exception('Recipe must be based on a package recipe!')

        parent_recipe = self.read_recipe(parent_recipe_path)

        # Determine our recipe's filename.
        self.recipe_name = parent_recipe_name.replace('.pkg.', '.jss.')
        self.recipe_name = self.prompt_for_value('Recipe Filename',
                                                 [self.recipe_name],
                                                 self.recipe_name)

        # Determine our recipe's identifier, and parent.
        parent_recipe_identifier = parent_recipe['Identifier']
        self.recipe_identifier = parent_recipe_identifier.replace(
            '.pkg.', '.jss.')
        self.recipe_identifier = self.prompt_for_value('Recipe Identifier',
                                                       [self.recipe_identifier],
                                                       self.recipe_identifier)
        self.parent_recipe = parent_recipe_identifier

        # Determine our product name, recipe description
        self.name = parent_recipe['Input']['NAME']
        self.recipe_description = (parent_recipe['Description'] +
            " Then, uploads to the JSS.")

        self.minimum_version = parent_recipe['MinimumVersion']

        # Use our parent recipe and JSS to prompt for information.
        jss_prefs = jss.JSSPrefs()
        j = jss.JSS(jss_prefs)

        # Check for any defaults set in RecipeTemplate (Put an un-escaped
        # category name in for your value).
        recipe_template = self.read_recipe(DEFAULT_RECIPE_TEMPLATE)
        categories = [cat.name for cat in j.Category()]

        recipe_template_pkg_category = recipe_template['Input']['CATEGORY']
        if '%' in recipe_template_pkg_category:
            # This is not a default value.
            self.pkg_category = self.prompt_for_value(
                'Package Category', categories)
        else:
            print('\nRecipe Template specified PKG_CATEGORY: %s\n' %
                  recipe_template_pkg_category)
            self.package_category = recipe_template_pkg_category

        recipe_template_policy_category = \
                recipe_template['Input']['POLICY_CATEGORY']
        if '%' in recipe_template_policy_category:
            # This is not a default value.
            self.policy_category = self.prompt_for_value(
                'Policy Category', categories)
        else:
            print('\nRecipe Template specified POLICY_CATEGORY: %s\n' %
                  recipe_template_policy_category)
            self.policy_category = recipe_template_policy_category

        # Policy template.
        template_options = [template for template in os.listdir(os.curdir) if
                            'XML' in os.path.splitext(template)[1].upper()]
        if DEFAULT_POLICY_TEMPLATE in template_options:
            default = DEFAULT_POLICY_TEMPLATE
        else:
            default = ''
        self.policy_template = self.prompt_for_value('Policy Template',
                                                     template_options,
                                                     default=default)

        # Group template.
        if DEFAULT_GROUP_TEMPLATE in template_options:
            default = DEFAULT_GROUP_TEMPLATE
        else:
            default = ''
        self.group_template = self.prompt_for_value('Group Template',
                                                     template_options,
                                                     default=default)

        # Icon (We only use png).
        default = self.name + '.png'
        icon_options = [icon for icon in os.listdir(os.curdir) if
                        'PNG' in os.path.splitext(icon)[1].upper()]
        self.icon = self.prompt_for_value('Self Service Icon',
                                                     icon_options,
                                                     default=default)

        # Product description.
        self.product_description = self.prompt_for_value(
            'Product Description', [], '')

        self.recipe = self.build_recipe()

    def read_recipe(self, path):
        """Read a recipe into a dict"""

        if not (os.path.isfile(path)):
			raise Exception("File does not exist: %s" % path)
        info, format, error = \
            NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
                NSData.dataWithContentsOfFile_(path),
                NSPropertyListMutableContainers,
                None,
                None
            )
        if error:
            raise Exception("Can't read %s: %s" % (path, error))

        return info

    def prompt_for_value(self, heading, options, default=None):
        """Ask user to choose from a list of choices.

        heading:            The name of the things (e.g. Category, Icon).
        options:            List of potential values string "name" values.
        default:            The default choice (to accept, hit enter).

        """
        print("Please choose a %s" % heading)
        print("Hit enter to accept default choice, or enter a number.")
        # We're not afraid of zero-indexed lists!
        counter = 0
        for option in options:
            choice_string = "%s: %s" % (counter, option)
            if default == option:
                choice_string += " (DEFAULT)"
            print(choice_string)
            counter += 1

        print("\nCreate a new %s by entering name/path." % heading)
        choice = raw_input("Choose and perish: (DEFAULT \'%s\') " % default)

        if choice.isdigit():
            result = options[int(choice)]
        elif choice == '':
            result = default
        else:
            # User provided a new object value.
            result = choice

        return result

    def build_recipe(self, recipe_template_path=DEFAULT_RECIPE_TEMPLATE):
        """Given a recipe template, swap in all of the
        values we have set up.

        """
        with open(recipe_template_path, 'r') as f:
            recipe = self.replace_text(f.read())
        return recipe

    def replace_text(self, text):
        """Substitute items in a text string.

        text: A string with embedded %tags%.

        """
        # Build a replacement dictionary
        replace_dict = {}
        replace_dict['%RECIPE_IDENTIFIER%'] = self.recipe_identifier
        replace_dict['%PARENT_RECIPE%'] = self.parent_recipe
        # The input variable substitution %NAME% is already used.
        replace_dict['%PRODUCT_NAME%'] = self.name
        replace_dict['%RECIPE_DESCRIPTION%'] = self.recipe_description
        replace_dict['%RECIPE_PRODUCT_DESCRIPTION%'] = self.product_description
        replace_dict['%MINIMUM_VERSION%'] = self.minimum_version
        replace_dict['%RECIPE_PKG_CATEGORY%'] = self.pkg_category
        replace_dict['%RECIPE_POLICY_CATEGORY%'] = self.policy_category
        replace_dict['%RECIPE_POLICY_TEMPLATE%'] = self.policy_template
        replace_dict['%RECIPE_GROUP_TEMPLATE%'] = self.group_template
        replace_dict['%RECIPE_ICON%'] = self.icon
        for key, value in replace_dict.iteritems():
            text = text.replace(key, value)
        return text


def main():
    """Commandline processing of JSSRecipeCreator."""
    recipe = JSSRecipeCreator(sys.argv[1])
    print(recipe.recipe)
    with open(recipe.recipe_name, 'w') as f:
        f.write(recipe.recipe)


if __name__ == '__main__':
    main()
