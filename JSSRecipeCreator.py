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

import argparse
import os.path
import pprint
import readline
import subprocess
import sys

from Foundation import (NSData,
                        NSPropertyListSerialization,
                        NSPropertyListMutableContainers,
                        NSPropertyListXMLFormat_v1_0)

import jss


# Globals
# Edit these if you want to change their default values.
# TODO: Potentially build a preferences/plist system to handle this.
DEFAULT_RECIPE_TEMPLATE = 'RecipeTemplate.xml'
DEFAULT_POLICY_TEMPLATE = 'PolicyTemplate.xml'
DEFAULT_RECIPE_DESC_PS = " Then, uploads to the JSS."
DEFAULT_GROUP_NAME = '%NAME%-update-smart'
DEFAULT_GROUP_TEMPLATE = 'SmartGroupTemplate.xml'
AUTOPKG_PREFERENCES = '~/Library/Preferences/com.github.autopkg.plist'

__version__ = '0.0.4'


class Plist(dict):
    """Abbreviated plist representation (as a dict) with methods for reading,
    writing, and creating blank plists.

    """
    def __init__(self, filename=None):
        """Parses an XML file into a Recipe object."""
        self._xml = {}

        if filename:
            self.read_recipe(filename)
        else:
            self.new_plist()

    def __getitem__(self, key):
        return self._xml[key]

    def __setitem__(self, key, value):
        self._xml[key] = value

    def __delitem__(self, key):
        del self._xml[key]

    def __iter__(self):
        return iter(self._xml)

    def __len__(self):
        return len(self._xml)

    def __repr__(self):
        return dict(self._xml).__repr__()

    def __str__(self):
        return dict(self._xml).__str__()

    def read_recipe(self, path):
        """Read a recipe into a dict."""
        path = os.path.expanduser(path)
        if not (os.path.isfile(path)):
            raise Exception("File does not exist: %s" % path)
        info, format, error = \
            NSPropertyListSerialization.propertyListWithData_options_format_error_(
                NSData.dataWithContentsOfFile_(path),
                NSPropertyListMutableContainers,
                None,
                None
            )
        if error:
            raise Exception("Can't read %s: %s" % (path, error))

        self._xml = info

    def write_recipe(self, path):
        """Write a recipe to path."""
        plist_data, error = NSPropertyListSerialization.dataWithPropertyList_format_options_error_(
            self._xml,
            NSPropertyListXMLFormat_v1_0,
            0,
            None
        )
        if error:
            raise Exception(error)
        else:
            if plist_data.writeToFile_atomically_(path, True):
                return
            else:
                raise Exception("Failed writing data to %s" % data)

    def new_plist(self):
        """Generate a barebones recipe plist."""
        pass


class Recipe(Plist):
    """Represents a recipe plist file, with methods for reading existing
    recipes and saving them again. Overrides dict, so most idioms and patterns
    apply.

    """
    def new_plist(self):
        """Generate a barebones recipe plist."""
        # Not implemented
        self._xml['Description'] = ''
        self._xml['Identifier'] = ''
        self._xml['MinimumVersion'] = ''
        self._xml['ParentRecipe'] = ''
        self._xml['Input'] = {}

        # JSSImporter-related Input variables
        self._xml['Input'].update({'NAME': '',
                                   'CATEGORY': '',
                                   'POLICY_CATEGORY': '',
                                   'POLICY_TEMPLATE': '',
                                   'ICON': '',
                                   'DESCRIPTION': ''})
        self._xml['Process'] = [{'Processor': 'JSSImporter',
                                 'Arguments': {'prod_name': '%NAME%',
                                               'category': '%CATEGORY%',
                                               'policy_category':
                                               '%POLICY_CATEGORY%',
                                               'policy_template':
                                               '%POLICY_TEMPLATE%',
                                               'self_service_icon': '%ICON%',
                                               'self_service_description':
                                               '%DESCRIPTION%',
                                               'groups': [] }}]


class JSSRecipe(Recipe):
    """Quickly build a jss recipe from a parent recipe."""
    #def __init__(self, parent_recipe_path, recipe_template_path):
    #    """Given a path to a parent recipe, pull all needed information.

    #    parent_recipe_path should be a path to a *pkg* recipe.

    #    Configures basic information about recipe, and then delegates other
    #    tasks to individual methods.

    #    """

    def handle_name(self):
        pass

    def handle_categories(self):
        # Check for any defaults set in RecipeTemplate (Put an un-escaped
        # category name in for your value).
        recipe_template = self.read_recipe(recipe_template_path)
        categories = [cat.name for cat in self.j.Category()]

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

    def handle_policy_template(self):
        pass

    def handle_group(self):
        # Icon (We only use png).
        default = self.name + '.png'
        icon_options = [icon for icon in os.listdir(os.curdir) if
                        'PNG' in os.path.splitext(icon)[1].upper()]
        self.icon = self.prompt_for_value('Self Service Icon',
                                                     icon_options,
                                                     default=default)

    def handle_description(self):
        # Product description.
        self.product_description = self.prompt_for_value(
            'Product Description', [], '')

    def handle_groups(self):
        """Present user with a menu for adding an arbitrary number of groups.
        For each group desired, we need a name, and whether the group is
        smart or not (and if smart, we need a SmartGroupTemplate).
        The RecipeCreator will then add an Input Variable for each group,
        as well as an array item in the JSSImporter/Arguments/Groups
        section, so that users can override the values if needed.
        The AutoPkg env is checked to ensure there aren't any foreseeable
        name collisions.

        """

        # Figure out which groups are already available on the JSS
        self.jss_groups = [group.name for group in self.j.ComputerGroup()]

        choice = raw_input('Would you like to add a scoping group? (Y|N) ')
        while str(choice).upper() != 'N':
            self.groups.append(self.group_menu())
            choice = raw_input('Would you like to add another scoping group?'
                               '(Y|N) ')

        #recipe_template_groups = [processor['Arguments']['groups'] for processor in recipe_template['Process'] if processor['Processor'] == 'JSSImporter']
        #self.group_name = self.prompt_for_value('Group Name', groups,)

    def group_menu(self):
        print('Enter name of group, substition variable to use (enclosed in'
              '" %% "), or hit enter to use the default name %s:' %
              DEFAULT_GROUP_NAME)
        #name = raw_input('(name|%%variable%%|Enter for %s) ' %
        #                 DEFAULT_GROUP_NAME)
        name = self.prompt_for_value('name', self.jss_groups,
                                     default=DEFAULT_GROUP_NAME)

        if DEFAULT_GROUP_TEMPLATE in self.template_options:
            default = DEFAULT_GROUP_TEMPLATE
        else:
            default = ''
        smart = raw_input('Should the group be "Smart"? (Y|N) ')
        if smart.upper() == 'Y':
            smart_group_template = self.prompt_for_value('Group Template',
                                                     self.template_options,
                                                     default=default)
        else:
            smart_group_template = None

        return {'name': name, 'smart_group_template': smart_group_template}


    # Deprecated
    def build_recipe(self, recipe_template_path=DEFAULT_RECIPE_TEMPLATE):
        """Given a recipe template, swap in all of the
        values we have set up.

        """
        # Do simple text replacement on templated variables
        with open(recipe_template_path, 'r') as f:
            recipe = self.replace_text(f.read())

        # Reopen as an XML document and inject the groups
        raise NotImplementedError("Not done yet")

        self.recipe = recipe

    # Deprecated
    def replace_text(self, text):
        """Substitute items in a text string.

        text: A string with embedded %tags%.

        """
        # Build a replacement dictionary
        replace_dict = {}
        replace_dict['%RECIPE_IDENTIFIER%'] = self.recipe_identifier
        replace_dict['%PARENT_RECIPE%'] = self.parent_recipe_identifier
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


class Menu(object):
    """Presents users with a menu and handles their input."""
    def __init__(self):
        self.submenus = []
        self.results = {}

    def run(self):
        for submenu in self.submenus:
            self.results.update(submenu.ask())

    def add_submenu(self, submenu):
        if isinstance(submenu, Submenu):
            self.submenus.append(submenu)
        else:
            raise Exception("Only Submenu may be added!")


class Submenu(object):
    """Represents an individual menu 'question'."""
    def __init__(self, heading, options, default=''):
        """Create a submenu.

        heading:            The name of the things (e.g. Category, Icon).
        options:            List of potential values string "name" values. Will
                            also accept a single value.
        default:            The default choice (to accept, hit enter).

        """
        self.heading = heading
        if not isinstance(options, list):
            self.options = [options]
        else:
            self.options = options
        self.default = default

    def ask(self):
        """Ask user a question based on configured values."""
        print("\nPlease choose a %s" % self.heading)
        print("Hit enter to accept default choice, or enter a number.\n")

        # We're not afraid of zero-indexed lists!
        indexes = xrange(len(self.options))
        option_list = zip(indexes, self.options)
        # Use zip!
        for option in option_list:
            choice_string = "%s: %s" % option
            if self.default == option[1]:
                choice_string += " (DEFAULT)"
            print(choice_string)

        print("\nCreate a new %s by entering name/path." % self.heading)
        choice = raw_input("Choose and perish: (DEFAULT \'%s\') " %
                           self.default)

        if choice.isdigit():
            result = self.options[int(choice)]
        elif choice == '':
            result = self.default
        else:
            # User provided a new object value.
            result = choice

        return {self.heading: result}


def configure_jss(env):
    """Configure a JSS object."""
    repoUrl = env["JSS_URL"]
    authUser = env["API_USERNAME"]
    authPass = env["API_PASSWORD"]
    sslVerify = env.get("JSS_VERIFY_SSL", True)
    suppress_warnings = env.get("JSS_SUPPRESS_WARNINGS", False)
    repos = env.get("JSS_REPOS")
    j = jss.JSS(url=repoUrl, user=authUser, password=authPass,
                ssl_verify=sslVerify, repo_prefs=repos,
                suppress_warnings=suppress_warnings)


def main():
    """Commandline processing of JSSRecipeCreator."""

    # Create our argument parser
    parser = argparse.ArgumentParser(description="Quickly generate JSS "
                                     "recipes.")
    parser.add_argument("ParentRecipe", help="Path to a parent recipe.")

    # This part is kind of confusing:
    # We have two options-build a JSSRecipe procedurally, or read in a recipe
    # template. But we also want to not HAVE to specify a template, since
    # most people will want to use one. So, we create a mutually exclusive
    # group. If you don't specify either of the -r or -s options, it uses the
    # default recipe template as specified in the global above. If you specify
    # both argparse stops execution. The only other case we need to worry about
    # is a defaulted -r value AND -s being specified on the cmdline. This is
    # tested for in the logic later.
    recipe_template_parser = parser.add_mutually_exclusive_group()
    recipe_template_parser.add_argument(
        "-r", "--recipe_template", help="Use a recipe template. Defaults to a "
        "file named %s in the current directory," % DEFAULT_RECIPE_TEMPLATE,
        default=DEFAULT_RECIPE_TEMPLATE)
    recipe_template_parser.add_argument(
        "-s", "--from_scratch", help="Do not use a recipe template; instead, "
        "build a recipe from scratch.", action='store_true')

    #parser.add_argument("-a", "--auto", help="Uses default choices for all "
    #                    "questions that have detected values. Prompts for "
    #                    "those which don't.", action='store_true')

    args = parser.parse_args()

    # Get AutoPkg configuration settings for python-jss/JSSImporter.
    env = Plist(AUTOPKG_PREFERENCES)
    configure_jss(env)

    # Build our interactive menu
    menu = Menu()

    # Filename.
    if not 'PKG.RECIPE' in args.ParentRecipe.upper():
        raise Exception('Recipe must be based on a package recipe!')
    parent_recipe = Recipe(args.ParentRecipe)
    default_filename = args.ParentRecipe.replace('.pkg.', '.jss.')
    menu.add_submenu(Submenu('Recipe Filename', default_filename,
                             default_filename))

    # Identifier
    parent_recipe_id = parent_recipe['Identifier']
    default_recipe_id = parent_recipe_id.replace('.pkg.', '.jss.')
    menu.add_submenu(Submenu('Recipe Identifier', default_recipe_id,
                             default_recipe_id))

    # Description, Min version.
    # Append a JSS recipe description to the parent's string.
    menu.results['Description'] = (parent_recipe['Description'] +
                                   DEFAULT_RECIPE_DESC_PS)

    # Use the parent's Minimum version since JSSImporter has no extra
    # version requirements.
    menu.results['minimum_version'] = parent_recipe['MinimumVersion']

    # NAME
    parent_recipe_NAME = parent_recipe['Input'].get('NAME', '')
    menu.add_submenu(Submenu('Name', parent_recipe_NAME,
                     parent_recipe_NAME))

    # Policy Template
    policy_template_options = [template for template in os.listdir(os.curdir)
                               if 'XML' in
                               os.path.splitext(template)[1].upper()]
    if DEFAULT_POLICY_TEMPLATE in policy_template_options:
        policy_template_default = DEFAULT_POLICY_TEMPLATE
    else:
        policy_template_default = ''
    menu.add_submenu(Submenu('Policy Template', policy_template_options,
                             policy_template_default))

    # Needs special handling
    menu.add_submenu(Submenu('Group', None, None))
    menu.add_submenu(Submenu('Self Service Description', None, None))

    menu.run()
    pprint.pprint(menu.results)

    # Create a JSSRecipe object and use our menu results to populate.
    # from_scratch and recipe_template are mutually exclusive
    if args.from_scratch:
        recipe = JSSRecipe()
    else:
        recipe = JSSRecipe(args.recipe_template)

    pprint.pprint(recipe)

    ######################################################################
    # Reference Code
    #    self.handle_group()
    #    self.handle_description()
    #    self.handle_groups()

    # Parent Recipe
    #    self.parent_recipe_path = parent_recipe_path
    #    self.recipe_template_path = recipe_template_path

    #    if self.recipe_template_path:
    #        self.recipe = Recipe(self.recipe_template_path)
    #    else:
    #        self.recipe = Recipe()

    #recipe = JSSRecipeCreator(args.ParentRecipe, args.recipe_template)
    #print(recipe.recipe)
    #recipe.recipe.write_recipe(recipe.recipe_name)
    #with open(recipe.recipe_name, 'w') as f:
    #    f.write(recipe.recipe)

    #print("Checking plist syntax...")
    #subprocess.check_call(['plutil', '-lint', recipe.recipe_name])


if __name__ == '__main__':
    main()
