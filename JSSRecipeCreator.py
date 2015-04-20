#!/usr/bin/python
# Copyright (C) 2014 Shea G Craig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""JSSRecipeCreator.py

Quickly create JSS recipes from a template.

usage: JSSRecipeCreator.py [-h] [-r RECIPE_TEMPLATE | -s] [-a] ParentRecipe

positional arguments:
  ParentRecipe          Path to a parent recipe.

optional arguments:
  -h, --help            show this help message and exit
  -r RECIPE_TEMPLATE, --recipe_template RECIPE_TEMPLATE
                        Use a recipe template. Defaults to a file named
                        RecipeTemplate.xml in the current directory,
  -s, --from_scratch    Do not use a recipe template; instead, build a
                        recipe from scratch.
  -a, --auto            Uses default choices for all questions that have
                        detected values. Prompts for those which don't.
"""


import argparse
import os.path
import readline  # pylint: disable=unused-import
import subprocess

# pylint: disable=no-name-in-module
from Foundation import (NSData,
                        NSPropertyListSerialization,
                        NSPropertyListMutableContainersAndLeaves,
                        NSPropertyListXMLFormat_v1_0)
# pylint: enable=no-name-in-module

import jss


# Globals
# Edit these if you want to change their default values.
AUTOPKG_PREFERENCES = "~/Library/Preferences/com.github.autopkg.plist"
PREFERENCES = os.path.expanduser("~/Library/Preferences/com.github.sheagcraig.JSSRecipeCreator.plist")

__version__ = "1.0.1"


class Error(Exception):
    """Module base exception."""
    pass


class ChoiceError(Error):
    """An invalid choice was made."""
    pass


class PlistParseError(Error):
    """Error parsing a plist file."""
    pass


class PlistDataError(Error):
    """Data can not be serialized to plist."""
    pass


class PlistWriteError(Error):
    """Error writing a plist file."""
    pass


class Plist(dict):
    """Abbreviated plist representation (as a dict)."""

    def __init__(self, filename=None):
        """Init a Plist, optionally from parsing an existing file.

        Args:
            filename: String path to a plist file.
        """
        if filename:
            dict.__init__(self, self.read_file(filename))
        else:
            dict.__init__(self)
            self.new_plist()

    def read_file(self, path):
        """Replace internal XML dict with data from plist at path.
        Args:
            path: String path to a plist file.

        Raises:
            PlistParseError: Error in reading plist file.
        """
        # pylint: disable=unused-variable
        info, pformat, error = (
            NSPropertyListSerialization.propertyListWithData_options_format_error_(
                NSData.dataWithContentsOfFile_(os.path.expanduser(path)),
                NSPropertyListMutableContainersAndLeaves,
                None,
                None
            ))
        # pylint: enable=unused-variable
        if info is None:
            if error is None:
                error = "Invalid plist file."
            raise PlistParseError("Can't read %s: %s" % (path, error))

        return info

    def write_plist(self, path):
        """Write plist to path.

        Args:
            path: String path to desired plist file.

        Raises:
            PlistDataError: There was an error in the data.
            PlistWriteError: Plist could not be written.
        """
        plist_data, error = NSPropertyListSerialization.dataWithPropertyList_format_options_error_(
            self,
            NSPropertyListXMLFormat_v1_0,
            0,
            None)
        if plist_data is None:
            if error is None:
                error = "Failed to serialize data to plist."
            raise PlistDataError(error)
        else:
            if not plist_data.writeToFile_atomically_(
                    os.path.expanduser(path), True):
                raise PlistWriteError("Failed writing data to %s" % path)

    def new_plist(self):
        """Generate a barebones recipe plist."""
        # Not implemented at this time.
        pass


class Recipe(Plist):
    """Represents a recipe plist file, with methods for reading existing
    recipes and saving them again. Overrides dict, so most idioms and
    patterns apply. Extends Plist.
    """
    def __init__(self, filename=None):
        """Init a Recipe, optionally from parsing an existing file.

        Args:
            filename: String path to a plist file.
        """
        super(Recipe, self).__init__(filename)

        # Ensure recipe has required keys.
        required_keys = ["Identifier", "Input", "Process"]
        for key in required_keys:
            if key not in self:
                raise PlistDataError("Recipe is lacking required key: %s" %
                                     key)

    def new_plist(self):
        """Generate a barebones recipe plist."""
        self["Description"] = ""
        self["Identifier"] = ""
        self["MinimumVersion"] = ""
        self["ParentRecipe"] = ""
        self["Input"] = {}

    def add_input_var(self, key, value=""):
        """Add or set a recipe input variable.

        Will set value if input variable already exists.

        Args:
            key: String name of input variable.
            value: Valid Plist format value for key.
        """
        self["Input"][key] = value


class JSSRecipe(Recipe):
    """An Autopkg JSS recipe. Extends Recipe.

    Recipes are constructed with redundant INPUT variables / JSSImporter
    arguments to maximize override-ability. Therefore, the JSSImporter
    arguments should be probably be left with replacement variables as
    their values.
    """
    def __init__(self, filename=None):
        """Init a JSSRecipe, optionally from parsing an existing file.

        Validates that recipe has a JSSImporter processor with required
        values.

        Args:
            filename: String path to a plist file.
        """
        super(JSSRecipe, self).__init__(filename)
        # Ensure a JSSImporter processor has been included in template.
        try:
            self.jss_importer = [processor for processor in
                                 self["Process"] if
                                 processor["Processor"] == "JSSImporter"].pop()
        except IndexError:
            raise PlistDataError("Recipe template is missing a JSSImporter")

    def new_plist(self):
        """Construct a new, empty JSS recipe.

        All JSSImporter arguments are exposed as Input Variables
        to ensure access through overrides.
        """
        super(JSSRecipe, self).new_plist()
        self["Input"].update({"NAME": "",
                              "CATEGORY": "",
                              "POLICY_CATEGORY": "",
                              "POLICY_TEMPLATE": "",
                              "ICON": "",
                              "DESCRIPTION": ""})
        self["Process"] = [{"Processor": "JSSImporter",
                            "Arguments": {"prod_name": "%NAME%",
                                          "category": "%CATEGORY%",
                                          "policy_category":
                                          "%POLICY_CATEGORY%",
                                          "policy_template":
                                          "%POLICY_TEMPLATE%",
                                          "self_service_icon": "%ICON%",
                                          "self_service_description":
                                              "%DESCRIPTION%",
                                          "groups": []}}]

    def add_scoping_group(self, group):
        """Add a group to the scope if it's not already included.

        Args:
            group: Group dict with items:
                name: String group name
                smart:  Bool True for smart groups, False for static.
                template_path: String relative path to template file.
        """
        recipe_groups = [processor["Arguments"]["groups"] for processor in
                         self["Process"] if processor["Processor"] ==
                         "JSSImporter"][0]

        if group not in recipe_groups:
            recipe_groups.append(group)

    def update(self, update_dict, comment=None):
        """Updates a JSSRecipe's values from supplied dict.

        Args:
            update_dict: Dictionary of recipe values. Keys should match the
                desired INPUT variable name.
            comment: String to include as a top-level comment.
        """
        # This is tightly coupled with the INPUT variable key names I
        # have chosen. This would be a good target for the next
        # refactoring.
        self["Identifier"] = update_dict["Identifier"]
        self["ParentRecipe"] = update_dict["ParentRecipe"]
        self["Description"] = update_dict["Description"]
        self["MinimumVersion"] = update_dict["MinimumVersion"]
        if comment:
            self["Comment"] = comment
        # Input section
        self["Input"]["NAME"] = update_dict["NAME"]
        if update_dict["POLICY_TEMPLATE"]:
            self["Input"]["POLICY_TEMPLATE"] = ("%%RECIPE_DIR%%/%s" %
                                                update_dict["POLICY_TEMPLATE"])
        # If a blank policy template has been set, don't prepend
        # anything; we actually want nothing!
        else:
            self["Input"]["POLICY_TEMPLATE"] = ""
        self["Input"]["POLICY_CATEGORY"] = update_dict["POLICY_CATEGORY"]
        self["Input"]["CATEGORY"] = update_dict["CATEGORY"]
        if update_dict["ICON"]:
            self["Input"]["ICON"] = "%%RECIPE_DIR%%/%s" % update_dict["ICON"]
        else:
            self["Input"]["ICON"] = ""
        self["Input"]["DESCRIPTION"] = update_dict["DESCRIPTION"]

        # Handle groups
        for group in update_dict["groups"]:
            self.add_scoping_group(group)


class Menu(object):
    """Presents users with a menu and handles their input.

    Submenus are managed in a list. run() and run_auto() will ask
    questions in order.

    Attributes:
        submenus: List of submenus Menu controls.
        results: Set of results.
    """

    def __init__(self):
        self.submenus = []
        self.results = {}

    def run(self, auto):
        """Run, in order, through our submenus, asking questions.

        Updates results after handling questions.

        Args:
            auto: Bool indicating whether to automatically use any
                default values.
        """
        for submenu in self.submenus:
            while True:
                try:
                    result = submenu.ask(auto=auto)
                    break
                except ChoiceError:
                    print "\n**Invalid entry! Try again.**"
                    continue
            self.results.update(result)

    def add_submenu(self, submenu):
        """Add a Submenu to our questions list.

        Args:
            submenu: Submenu object of questions.

        Raises:
            TypeError: If non-Submenu added.
        """
        if isinstance(submenu, Submenu):
            self.submenus.append(submenu)
        else:
            raise TypeError("Only Submenu may be added!")


# pylint: disable=too-few-public-methods
class Submenu(object):
    """Represents an individual menu 'question'."""
    OPTIONAL_ARG = "<None>"

    def __init__(self, key, options, optional, default="", heading=""):
        """Create a submenu.

        Args:
            key: String Name of INPUT variable key.
            options: List of potential string values to populate
                submenu choices. Will also accept a single value.
            optional: Bool indicating whether this is a required arg
                for the recipe. If optional is True, will add a <None>
                value to the menu options.
            default: String default choice. User hits enter to accept.
                Defaults to having no default.
            heading: String name to use as a heading, (e.g. Category,
                Icon). Defaults to using the key name.
        """
        self.key = key
        self.options = []
        # If we don't get a heading, just use the key name.
        if not heading:
            self.heading = key
        else:
            self.heading = heading
        if not isinstance(options, list):
            self.options.append(options)
        else:
            self.options.extend(options)
        if optional:
            self.options.insert(0, self.OPTIONAL_ARG)
        self.default = default

    def ask(self, auto=False):
        """Ask user a question based on configured values.

        Args:
            auto: Bool. If True, and a default value has been provided,
                use that default value.

        Returns:
            Dict with key = self.key and val = the user's choice.

        Raises:
            ChoiceError: User has made an invalid choice.
        """
        if auto and self.default:
            result = self.default
        else:
            print_heading("%s Menu" % self.heading)
            self.display_options_list(self.options, default=self.default)

            print "\nHit enter to accept default choice."
            print "Enter a number to select from list."
            print "Create a new %s by entering name/path.\n" % self.heading
            choice = raw_input("Please choose a %s: (DEFAULT \'%s\') " %
                               (self.heading, self.default))

            if choice.isdigit() and in_range(int(choice), len(self.options)):
                result = self.options[int(choice)]
                if result == self.OPTIONAL_ARG:
                    result = ""
            elif choice == "":
                result = self.default
            elif choice.isdigit() and not in_range(int(choice),
                                                   len(self.options)):
                raise ChoiceError("Invalid Choice.")
            else:
                # User provided a new object value.
                result = choice

        return {self.key: result}

    def display_options_list(self, options, default=""):
        """Prints options in columns as a numbered list.

        Args:
            options: Iterable of strings to enumerate, and print in
                columns.
            default: String value to mark as a default.
        """
        # We're not afraid of zero-indexed lists!
        if default in options:
            options[options.index(default)] += " (DEFAULT)"

        # Get the length of the longest index number, plus an indent.
        length = len(str(len(options))) + 4
        fmt_string = "{0[0]:>{length}}: {0[1]}"
        choices = "\n".join([fmt_string.format(option, length=length) for
                             option in enumerate(options)])
        print choices

# pylint: enable=too-few-public-methods


class ScopeSubmenu(Submenu):
    """Specialized submenu for scope questions."""
    # Group type typedef.
    STATIC_GROUP = False
    SMART_GROUP = True

    def __init__(self, recipe_template, j, env):
        """Prepare menu with data from template and JSS.

        Args:
            recipe_template: A Recipe object (NSCFDictionary).
            j: A jss.JSS object to poll for existing groups.
        env: Dict with optional item "Default_Group_Template". Meant to
            be passed the JSSRecipeCreator environment dict.
        """
        self.recipe_template = recipe_template
        self.j = j
        self.env = env

        # Let's see what groups are available on the JSS.
        self.jss_groups = [group.name for group in self.j.ComputerGroup()]

        # Set up a list for storing desired groups to add, and grab the
        # templated groups to add to it.
        # Entries should be a dict of name, smart, and
        # template_path values.
        self.results = []
        if "groups" in recipe_template.jss_importer["Arguments"].keys():
            templated_groups = recipe_template.jss_importer["Arguments"].get(
                "groups")
            self.results.extend(templated_groups)

    def ask(self, auto=False):
        """Ask user about scoping based on configured values.

        Offers users a list of groups found on the JSS, as well as the
        ability to create new groups. This menu allows use of
        substitution variables as well.

        Args:
            auto: Bool. If True, and a default value has been provided,
                use that default value.

        Returns:
            Dict with key "groups", with value a list of group dicts.
                group dicts include keys:
                    name: String name of group
                    smart: Bool indicating Smart or Static group.
                    template_path (optional): Relative path to group
                        template file.

        Raises:
            ChoiceError: User has made an invalid choice.
        """
        if not auto:
            template_list = [template for template in os.listdir(os.curdir) if
                             os.path.splitext(template)[1].upper() == ".XML"]
            while True:
                print_heading("Scope Menu")
                print "Groups available on the JSS:"
                self.display_options_list(self.jss_groups)
                print_heading("Current Scope")
                self.display_results()
                print ("\nTo add a new group, enter a new name. You may use "
                       "substitution variables.")
                print ("To select an existing group, enter its ID above, or "
                       "its name.")
                print "To QUIT this menu, hit 'return'. "
                choice = raw_input("\nGroup command: ")

                # Handle primary group menu choice.
                if choice.isdigit() and in_range(int(choice),
                                                 len(self.jss_groups)):
                    name = self.jss_groups[int(choice)]
                elif choice == "":
                    break
                elif choice.isdigit() and not in_range(int(choice),
                                                       len(self.jss_groups)):
                    raise ChoiceError("Invalid Choice")
                else:
                    name = choice

                result = {"name": name}

                # Try to see if this group already exists, and if so,
                # whether it is smart or not.
                group_type = self._check_group(name)

                if group_type is None:
                    smart_choice = raw_input(
                        "Should this group be a smart group? (Y|N) ")
                    if smart_choice.upper() == "Y":
                        group_type = self.SMART_GROUP
                    else:
                        group_type = self.STATIC_GROUP
                result["smart"] = group_type

                if group_type is self.SMART_GROUP:
                    result["template_path"] = (
                        self._get_smart_group_template(template_list))

                self.results.append(result)

        return {"groups": self.results}

    def _get_smart_group_template(self, template_list):
        """Ask user which smart group template to use."""
        default = self.env.get("Default_Group_Template", "")
        print_heading("Smart Group Template")
        self.display_options_list(template_list, default)

        print ("\nChoose a template by selecting an ID, or entering a "
               "filename.\n")
        template_choice = raw_input(
            "Select a group template: (DEFAULT '%s') " % default)

        if template_choice.isdigit() and in_range(
                int(template_choice), len(template_list)):
            template = template_list[int(template_choice)]
        elif template_choice == "":
            if default:
                template = default
            else:
                raise ChoiceError("Invalid choice. A template is required.")
        elif template_choice.isdigit() and not in_range(
                int(template_choice), len(template_list)):
            raise ChoiceError("Invalid choice.")
        else:
            template = template_choice

        # Prepend %RECIPE_DIR% so recipes always know where to find
        # template.
        return "%RECIPE_DIR%/" + template

    def _check_group(self, name):
        """Check for whether a group exists, and if so, if it is smart.

        Args:
            name: The name of the group to check.

        Returns:
            JSSRecipe.STATIC_GROUP if group is static,
            JSSRecipe.SMART_GROUP if group is smart, or None if group
            doesn't exist.
        """
        try:
            group = self.j.ComputerGroup(name)
        except jss.exceptions.JSSGetError:
            group = None

        if group is None:
            result = None
        elif group.findtext("is_smart") == "true":
            result = self.SMART_GROUP
        else:
            result = self.STATIC_GROUP

        return result

    def display_results(self):
        """Pretty print current results."""
        for result in self.results:
            if result["smart"]:
                print "Smart Group:"
            else:
                print "Static Group:"
            print "\n".join(["    %s: %s" % (item, result[item]) for item in
                             result])


def configure_jss(env):
    """Configure a JSS object based on JSSRecipeCreator's env.

    Args:
        env: Dictionary of JSSRecipeCreator's env.
    Returns:
        Returns a python-jss JSS object.
    """
    repo_url = env["JSS_URL"]
    auth_user = env["API_USERNAME"]
    auth_pass = env["API_PASSWORD"]
    ssl_verify = env.get("JSS_VERIFY_SSL", True)
    suppress_warnings = env.get("JSS_SUPPRESS_WARNINGS", False)
    repos = env.get("JSS_REPOS")
    j = jss.JSS(url=repo_url, user=auth_user, password=auth_pass,
                ssl_verify=ssl_verify, repo_prefs=repos,
                suppress_warnings=suppress_warnings)
    return j


def build_menu(j, parent_recipe, recipe, parent_filename, env):
    """Construct the menu for prompting users to create a JSS recipe.

    Args:
        j: A python-jss JSS object.
        parent_recipe: Recipe of the desired parent recipe.
        recipe: JSSRecipe object to populate, either loaded from a
            recipe template, or as a new() JSSRecipe..
        args: Arguments returned from argparser.
        env: JSSRecipeCreator preferences dict.

    Returns:
        A Menu with all questions configured and ready to ask().

    Raises:
        AttributeError: If a non-pkg recipe is provided as the parent,
            as a pkg is required for policy installs.
    """
    menu = Menu()

    # Filename.
    if not "PKG.RECIPE" in parent_filename.upper():
        raise AttributeError("Recipe must be based on a package recipe!")
    default_filename = os.path.basename(
        parent_filename.replace(".pkg.", ".jss."))
    menu.add_submenu(Submenu("Recipe Filename", default_filename, False,
                             default=default_filename))

    # Identifier
    parent_recipe_id = parent_recipe["Identifier"]
    default_recipe_id = parent_recipe_id.replace(".pkg.", ".jss.")
    menu.add_submenu(Submenu("Identifier", default_recipe_id, False,
                             default=default_recipe_id,
                             heading="Recipe Identifier"))

    # Parent Recipe
    menu.results["ParentRecipe"] = parent_recipe["Identifier"]

    # NAME
    parent_recipe_name = parent_recipe["Input"].get("NAME", "")
    menu.add_submenu(Submenu("NAME", parent_recipe_name, False,
                             default=parent_recipe_name))

    # Description, Min version.
    # Append a JSS recipe description to the parent's string.
    menu.results["Description"] = (parent_recipe.get(
        "Description", "Builds a package of %s." %
        parent_recipe_name) + env.get("Default_Recipe_Desc_PS", ""))

    # Use the parent's Minimum version since JSSImporter has no extra
    # version requirements.
    menu.results["MinimumVersion"] = parent_recipe.get("MinimumVersion",
                                                       "0.4.2")

    # Policy Template
    policy_template_options = [template for template in os.listdir(os.curdir)
                               if "XML" in
                               os.path.splitext(template)[1].upper()]
    # Check for a value supplied in the template; then fall back to the
    # global from above, and barring that, use "".
    if recipe["Input"].get("POLICY_TEMPLATE"):
        policy_template_default = recipe["Input"]["POLICY_TEMPLATE"]
    elif (env.get("Default_Policy_Template") and
          env["Default_Policy_Template"] in policy_template_options):
        policy_template_default = env["Default_Policy_Template"]
    else:
        policy_template_default = ""
    menu.add_submenu(Submenu("POLICY_TEMPLATE", policy_template_options, True,
                             default=policy_template_default,
                             heading="Policy Template"))

    # Categories
    categories = [cat.name for cat in j.Category()]
    default_pkg_category = recipe["Input"].get("CATEGORY", "")
    menu.add_submenu(Submenu("CATEGORY", categories, True,
                             default=default_pkg_category,
                             heading="Package Category"))
    default_policy_category = recipe["Input"].get("POLICY_CATEGORY", "")
    menu.add_submenu(Submenu("POLICY_CATEGORY", categories, True,
                             default=default_policy_category,
                             heading="Policy Category"))

    # Scope
    menu.add_submenu(ScopeSubmenu(recipe, j, env))

    # Icon (We only use png).
    icon_default = parent_recipe["Input"].get("NAME", "Icon") + ".png"
    icon_options = [icon for icon in os.listdir(os.curdir) if
                    "PNG" in os.path.splitext(icon)[1].upper()]
    if icon_default not in icon_options:
        icon_options.append(icon_default)
    menu.add_submenu(Submenu("ICON", icon_options, True, default=icon_default,
                             heading="Self Service Icon"))

    # Self Service description.
    default_self_service_desc = recipe["Input"].get("DESCRIPTION", "")
    menu.add_submenu(Submenu("DESCRIPTION",
                             default_self_service_desc, True,
                             default=default_self_service_desc,
                             heading="Self Service Description"))

    return menu


def build_argparser(env):
    """Create JSSRecipeCreator argument parser.

    Args:
        env: Dict of JSSRecipeCreator preferences.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(description="Quickly generate JSS "
                                     "recipes.")
    parser.add_argument("ParentRecipe", help="Path to a parent recipe.",
                        nargs="*")

    # This part is kind of confusing:
    # We have two options-build a JSSRecipe procedurally, or read in a
    # recipe template. But we also want to not HAVE to specify a
    # template, since most people will want to use one. So, we create a
    # mutually exclusive group. If you don't specify either of the -r or
    # -s options, it uses the default recipe template as specified in
    # the global above. If you specify both argparse stops execution.
    # The only other case we need to worry about is a defaulted -r value
    # AND -s being specified on the cmdline. This is tested for in the
    # logic later.
    recipe_template_parser = parser.add_mutually_exclusive_group()
    default_recipe_template = env.get("Default_Recipe_Template", "")
    recipe_template_parser.add_argument(
        "-r", "--recipe_template", help="Use a recipe template. Defaults to a "
        "file named %s in the current directory," %
        default_recipe_template, default=default_recipe_template)
    recipe_template_parser.add_argument(
        "-s", "--from_scratch", help="Do not use a recipe template; instead, "
        "build a recipe from scratch.", action="store_true")

    parser.add_argument("-a", "--auto", help="Uses default choices for all "
                        "questions that have detected values. Prompts for "
                        "those which don't.", action="store_true")

    return parser


def to_bool(val):
    """Convert string bool values to python Bool."""
    if val == "false":
        return False
    elif val == "true":
        return True
    else:
        raise ValueError()


def in_range(val, size):
    """Determine whether a value x is within the range 0 > x <= size."""
    return val < size and val >= 0


def get_preferences():
    """Ensure a preferences file exists, and open it.

    Uses global constant PREFERENCES to ensure that a folder with that
    path exists, and loads it as a Plist object. If needed, generates
    the default settings.

    Returns:
        Plist of preferences.
    """
    if os.path.exists(PREFERENCES):
        env = Plist(PREFERENCES)
    else:
        env = Plist()
        env["Default_Recipe_Template"] = "RecipeTemplate.xml"
        env["Default_Policy_Template"] = "PolicyTemplate.xml"
        env["Default_Recipe_Desc_PS"] = " Then, uploads to the JSS."
        env["Default_Group_Template"] = "SmartGroupTemplate.xml"
        env["Recipe_Comment"] = (
            "\nThis AutoPkg recipe was created using JSSRecipeCreator: "
            "\nhttps://github.com/sheagcraig/JSSRecipeCreator\n\n"
            "It is meant to be used with JSSImporter: \n"
            "https://github.com/sheagcraig/JSSImporter\n\n"
            "For tips on integrating JSSImporter into your Casper "
            "environment, check out Auto Update Magic:\n"
            "https://github.com/homebysix/auto-update-magic")
        env.write_plist(PREFERENCES)

    return env


def pprint(data, indent=4):
    """Pretty print a dictionary with indention."""
    for item in data:
        if isinstance(data, list):
            pprint(item, indent + 8)
            print
        elif isinstance(data[item], list):
            print indent * " " + "%15s:" % item
            pprint(data[item], indent + 8)
        else:
            print indent * " " + "%15s: %s" % (item, data[item])


def print_heading(heading, line_char="="):
    """Print a string, followed by a line of chars."""
    print "\n" + heading
    print (len(heading) - 1) * line_char


def main():
    """Commandline processing of JSSRecipeCreator."""
    # Get JSSRecipeCreator preferences.
    env = get_preferences()

    # Handle command line arguments
    parser = build_argparser(env)
    args = parser.parse_args()

    # Get AutoPkg configuration settings for python-jss/JSSImporter.
    autopkg_env = Plist(AUTOPKG_PREFERENCES)
    j = configure_jss(autopkg_env)

    for parent in args.ParentRecipe:
        print parent
        # Create a JSSRecipe object
        # from_scratch and recipe_template are mutually exclusive
        if args.from_scratch:
            recipe = JSSRecipe()
        else:
            recipe = JSSRecipe(args.recipe_template)

        # We need a parent recipe to use for determining some values.
        parent_recipe = Recipe(parent)
        # If the parent recipe uses PlistReader to determine version, we
        # need to add a blank version input var to the jss recipe to get
        # past the AutoPkg preprocessor.
        # Recipes may use multiple versioning processors. If either
        # Versioner or AppDmgVersioner are present, we probably don't need a
        # <version> tag.
        # Custom processors may also output version.
        # Without parsing each processor, this is the best we can do.
        # Thankfully, overriding <version> with a blank value won't unset
        # versions found earlier, so this is a safe assumption to make.
        parent_processors = [processor["Processor"] for processor in
                             parent_recipe["Process"]]
        if "PlistReader" in parent_processors:
            if "Versioner" not in parent_processors or ("AppDmgVersioner" not
                                                        in parent_processors):
                recipe.add_input_var("version")

        # Build our interactive menu
        menu = build_menu(j, parent_recipe, recipe, parent, env)

        # Run the questions past the user.
        menu.run(auto=args.auto)

        print_heading("Results")
        pprint(menu.results)

        # Merge the answers with the JSSRecipe.
        recipe.update(menu.results, env.get("Recipe_Comment", ""))
        recipe.write_plist(menu.results["Recipe Filename"])

        # Final output.
        print_heading("Lint")
        print "Checking plist syntax..."
        subprocess.check_call(["plutil", "-lint",
                               menu.results["Recipe Filename"]])
        print


if __name__ == "__main__":
    main()
