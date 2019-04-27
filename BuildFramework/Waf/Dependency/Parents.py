from __future__ import absolute_import, division, print_function

from waflib import Errors
from waflib import Logs
from waflib import Options
from waflib.Build import BuildContext

from Waf.Utilities import GetTargetProjects

## \package Waf.Dependency.Parents
## This package defines the 'parents' command and tools for gathering parents from task generators.

## Adds the options for the parents command.
## \param[in] options_context - The options context is shared by all user defined options methods.
def options(options_context):
    # CREATE AN OPTION GROUP FOR THE PARENT OPTIONS.
    parent_option_group = options_context.add_option_group("Parent options")

    # LOAD THE COMMAND LINE ARGUMENTS.
    # Add an option to print all dependencies.
    parent_option_group.add_option(
        '--allparents',
        action='store_true',
        default = False,
        help = 'Show all dependencies.')

## Returns the parents (immediate only, or all) of a given target project. Showing only the immediate parents
# supports creation and maintenance of Waf scripts. It can be used to determine if a project's dependencies
# are redundant. Showing all parents can assist in understanding the overall dependencies of a product.
class Parents(BuildContext):
    # The comment below provides the help text for the command-line.
    '''prints the dependencies of the target projects'''

    # Set the command name for the command-line.
    cmd = 'parents'

    # Gets the parents for the target project(s). The method disables the actual build.
    def execute_build(self):
        # PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        projects = GetTargetProjects(self)

        # PRINT THE PARENTS OF EACH OF THE TARGET.
        immediate_only = not Options.options.allparents
        for project in projects:
            Logs.info('{}: {}'.format(project.name, GetParents(project, immediate_only)))

## Gets the dependencies of the target project.
# \param    project - The task generator of the project for which to find parents.
# \param    immediate_only - Indicates whether only the immediate parents should be retrieved.
# \return   The sorted dependencies of the target project.
def GetParents(project, immediate_only):
    # CHECK WHETHER IMMEDIATE PARENTS WERE REQUESTED.
    if (immediate_only):
        # Return the sorted list of immediate parents.
        parent_names = GetImmediateParents(project)
        return sorted(parent_names)
    else:
        # Return the sorted list of all parents.
        all_parent_names = GetAllParents(project)
        return sorted(all_parent_names)

## Returns the immediate parents of the given project. Showing only the immediate parents
# supports creation and maintenance of Waf scripts. It can be used to determine if a project's dependencies
# are redundant.
# \param    project - The waf task whose immediate parents should be found.
# \return   The immediate parents of the project.
def GetImmediateParents(project):
    # GATHER THE DYNAMIC ATTRIBUTES.
    is_dynamic_attribute = lambda attribute_name: ('dynamic_' in attribute_name)
    dynamic_attribute_names = [
        attribute_name for attribute_name in dir(project)
        if is_dynamic_attribute(attribute_name)]

    # GET THE PARENTS OF THE PROJECT.
    # A project expresses parent dependencies using the 'use', 'depends_on', or 'runs_after'
    # attributes, or using a dynamic attribute.
    # The code_generator attribute is not included because it would pull in libraries that are
    # used to build the code generator, which the target project may not actually depend on.
    parent_names = set()
    parent_dependency_attribute_names = (
        ['use', 'depends_on', 'runs_after'] +
        dynamic_attribute_names)
    for parent_dependency_attribute_name in parent_dependency_attribute_names:
        # GATHER THE PARENTS.
        parent_names.update(project.to_list(getattr(
            project, parent_dependency_attribute_name, [])))

    return parent_names

## Returns all of the parents of the given project.
# \param    project - The waf task for which all parents should be found.
# \return   All of the parents of the project.
def GetAllParents(project):
    # GATHER THE IMMEDIATE PARENTS OF THE TARGET PROJECT.
    parent_names = GetImmediateParents(project)

    # UPDATE THE LIST OF ALL PARENT NAMES WITH THE IMMEDIATE PARENTS.
    all_parent_names = parent_names

    # GATHER THE REST OF THE PARENTS OF THE PROJECT.
    while parent_names:
        # GET THE PARENT NAMES IN THE NEXT TIER.
        next_parent_names = set()
        for parent_name in parent_names:
            # Get the project for the parent.
            try:
                parent_project = project.bld.get_tgen_by_name(parent_name)
            except Errors.WafError:
                continue

            # Get the immediate parents of this parent project.  These will be used for traversing
            # the next tier of parent projects.
            next_parent_names.update(GetImmediateParents(parent_project))

        # UPDATE THE LIST OF ALL PARENT NAMES WITH THE NEXT TIER OF PARENTS.
        all_parent_names.update(next_parent_names)

        # PREPARE FOR TRAVERSING THE NEXT TIER OF PARENTS.
        parent_names = next_parent_names

    return all_parent_names
