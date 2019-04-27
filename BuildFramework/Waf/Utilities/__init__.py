from __future__ import absolute_import, division, print_function

from distutils import spawn
import difflib
import hashlib
import itertools
import os
import subprocess
import sys
import uuid

from waflib import Logs
from waflib import Utils

## \package Waf.Utilities
## This package contains general commands used in the development work flow and utility functions
## used in many custom tools.

## Adds the options for current tool and all sub-tools. This method is executed before the current
## command context is initialized.
## \param[in] options_context - The options context is shared by all user defined options methods.
def options(options_context):
    LoadTools(options_context, __file__)

## Initializes the command context for the current tool and all sub-tools. This method is executed
## before the user defined command methods.
## \param[in] command_context - The command context is shared by all user defined initialization
## methods.
def init(command_context):
    LoadTools(command_context, __file__)

## Configures the environment for the current tool and all sub-tools.
## \param[in] configure_context - The configure context is shared by all user defined configure
## methods.
def configure(configure_context):
    LoadTools(configure_context, __file__)

## Loads the Waf tools in the directory of the currently executing Python script.
## \param[in] context - The current command context.
## \param[in] python_script_path - The path to the currently executing Python script.
def LoadTools(context, python_script_path):
    # GATHER THE WAF TOOLS IN THE CURRENT DIRECTORY.
    # The tools are a Waf thing with init, configure, etc. They define extensions to waf, or code
    # that should be run during commands.
    current_file_path = os.path.realpath(python_script_path)
    tool_dir_path = os.path.dirname(current_file_path)
    tool_names = []
    for file_name in os.listdir(tool_dir_path):
        # CHECK IF THE FILE IS A PYTHON SCRIPT.
        # A Waf tools is a Python script other than the currently executing Python script or a
        # Python module.
        file_path = os.path.join(tool_dir_path, file_name)
        is_python_script = (
            os.path.isfile(file_path) and
            file_path.endswith('.py'))
        is_python_module = (
            os.path.isdir(file_path) and
            os.path.isfile(os.path.join(file_path, '__init__.py')))
        is_waf_tool = (is_python_script or is_python_module)
        if not is_waf_tool:
            continue

        # CHECK IF THE FILE IS THE CURRENT WAF TOOL.
        # The current tool should not be loaded again.
        tool_name, python_ext = os.path.splitext(file_name)
        is_current_tool = (tool_name == '__init__')
        if is_current_tool:
            continue

        # STORE THE WAF TOOL NAME.
        tool_names.append(tool_name)

    # LOAD THE WAF TOOLS.
    # The method with the same name as the command of the current context will be executed.
    context.load(tool_names, tooldir = tool_dir_path)

## Generates a UUID using a MD5 hash. The UUID is returned in canonical form.
## For example, 550e8400-e29b-41d4-a716-446655440000
def UuidMd5Hash(text):
    unique_hash = hashlib.md5(text.encode()).hexdigest()
    unique_id = uuid.UUID(unique_hash, version = 4)
    unique_id_text = str(unique_id)
    return unique_id_text

## Returns the projects targeted by the given command. Targets are defined in
## two ways. First, they can be specified explicitly using the "--targets"
## option. Second, they can be specified implicitly by executing the command
## from a sub-directory.
## \param command_context - The context describes both how the command was
## executed and all projects in the build system.
## \returns The projects targeted by the given command.
def GetTargetProjects(command_context):
    # LOAD ALL PROJECTS.
    command_context.recurse([command_context.run_dir])
    projects = list(itertools.chain.from_iterable(command_context.groups))

    # TARGETS MAY BE SPECIFIED EXPLICITLY.
    targets_specified = command_context.targets
    if targets_specified:
        # THE USER CAN OVERRIDE THE SUB-DIRECTORY RESTRICTION.
        # From a sub-directory, the user can target all projects without having
        # navigate back to the root.
        all_projects_specified = (command_context.targets == '*')
        if all_projects_specified:
            return projects

        # PROJECTS ARE RESTRICTED TO THE SPECIFIED NAMES.
        target_names = set(command_context.targets.split(','))
        project_is_target = lambda project: project.name in target_names
        target_projects = [project for project in projects if project_is_target(project)]

        # DETERMINE WHICH TARGETS WEREN'T FOUND.
        target_project_names = set([project.name for project in target_projects])
        target_projects_not_found = target_names.difference(target_project_names)
        all_targets_found = (len(target_projects_not_found) == 0)
        if not all_targets_found:

            # Inform the user. Otherwise it's possible that no action will be performed,
            # which may not be immediately evident to the user.
            all_project_names = [project.name for project in projects]
            for not_found_project_name in list(target_projects_not_found):

                # Find similarly-named projects that the user may have mis-typed.
                # By default, the top 3 matches above the default 'close match' threshold will be returned.
                similar_project_names = difflib.get_close_matches(not_found_project_name, all_project_names)
                similar_project_names_found = (len(similar_project_names) > 0)

                # Indicate to the user that the target project wasn't found.
                warning_message = '{} not found!'.format(not_found_project_name)
                if (similar_project_names_found):
                    # Add possible alternatives to the message, putting each alternative on its own
                    # line, and indented for readability.
                    indented_similar_project_names_text = '\t' + '?\n\t'.join(similar_project_names) + '?'
                    suggested_alternates_text = 'Did you mean:\n{}'.format(indented_similar_project_names_text)
                    warning_message += (' ' + suggested_alternates_text)
                Logs.warn(warning_message)

        return list(target_projects)

    # PROJECTS ARE RESTRICTED TO THOSE BELOW THE LAUNCH DIRECTORY.
    # Code, tests, and utilities are often often developed in tandem. A user
    # can target the group without explicitly writing each name.
    project_is_child_of_launch_dir = lambda project: project.path.is_child_of(command_context.launch_node())
    child_projects = [project for project in projects if project_is_child_of_launch_dir(project)]

    # DETERMINE IF ANY CHILD PROJECTS WERE FOUND.
    any_child_projects_found = (len(child_projects) > 0)
    if not any_child_projects_found:
        # Inform the user. This could occur in a case where wscripts in the launch directory are not
        # applicable to the current build environment (e.g., projects are Linux-only, or only x86).
        Logs.warn("No projects found in {}".format(command_context.launch_node().abspath()))

    return child_projects

## Opens a file with its default application.
## \param   filepath - The path to the file to open.
def OpenFileInDefaultProgram(filepath):
    # Check if the operating system is Windows.
    if Utils.is_win32:
        # The file can simply be started.
        os.startfile(filepath)
    # Open the file with gnome-open if available.
    # All output is redirected to null to keep the console output clean.
    elif spawn.find_executable('gnome-open'):
        subprocess.call('gnome-open "{0}" &>/dev/null'.format(filepath), shell = True)
    # Open the file with xdg-open if available.
    # All output is redirected to null to keep the console output clean.
    elif spawn.find_executable('xdg-open'):
        subprocess.call('xdg-open "{0}" &>/dev/null'.format(filepath), shell = True)
    else:
        Logs.warn(filepath + " cannot be opened.")

## Retrieves the absolute path of the main waf script, "waf" (the entry point of the build system).
## \return  The absolute path to the main waf script.
def GetWafScriptFilepath():
    return os.path.abspath(sys.argv[0])

## Prints a short message with the enabled settings for the current waf variant.
## \param command_context - The context describes both how the command was
## executed and all projects in the build system.
def PrintWafSettings(command_context):
    # GATHER THE SETTINGS FROM THE COMMAND CONTEXT.
    current_variant_settings = []

    # Check if symbols are enabled.
    if command_context.env.SYMBOLS:
        current_variant_settings.append("symbols")

    # Check if optimization is enabled.
    if command_context.env.OPTIMIZE:
        current_variant_settings.append("optimize")

    # Check if obfuscation is enabled.
    if command_context.env.OBFUSCATE:
        current_variant_settings.append("obfuscate")

    # Check if code coverage is enabled.
    if command_context.env.CODE_COVERAGE:
        current_variant_settings.append("code coverage")

    # PRINT THE SETTINGS.
    summarized_settings = ", ".join(current_variant_settings) if current_variant_settings else "none"
    settings_message = "Variant '%s' (enabled settings: %s)" % (
        command_context.variant,
        summarized_settings)
    Logs.info(settings_message)
