from __future__ import absolute_import, division, print_function

from collections import namedtuple
import itertools
import os
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader
from waflib import Errors
from waflib import Options
from waflib import Utils
from waflib.Build import BuildContext

from Waf.IdeIntegration.CppProject import CppProject
from Waf.IdeIntegration.DotNetProject import DotNetProject
from Waf.IdeIntegration.FileExplorer import FileExplorer
from Waf.IdeIntegration.Project import Project
from Waf.Utilities import GetTargetProjects
from Waf.Utilities import GetWafScriptFilepath
from Waf.Utilities import OpenFileInDefaultProgram
from Waf.Utilities import UuidMd5Hash

## \package Waf.IdeIntegration.CodeBlocks
## This package defines command for generating project files for the Code::Blocks C++ IDE.

## This command generates project files for the Code::Blocks C++ IDE.
class CodeBlocksContext(BuildContext):
    # The comment below provides the help text for the command-line.
    '''generates a code::blocks workspace'''
    cmd = 'cbp'

    # Generates Code::Blocks projects and solutions. The method disables the
    # actual build.
    def execute_build(self):
        # LOAD THE TEMPLATE ENVIRONMENT.
        template_dir = self.path.find_node('BuildFramework/Waf/IdeIntegration')
        template_loader = FileSystemLoader(template_dir.abspath())
        template_env = Environment(
            loader = template_loader,
            trim_blocks = True,
            lstrip_blocks = True)

        # PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        projects = GetTargetProjects(self)

        # GENERATE CODE BLOCKS PROJECT FILES.
        workspace_dirs = set([])
        for project in projects:
            # LOAD THE PROJECT.
            project.post()

            # MAKE SURE THE PROJECT HAS USER WRITTEN FILES.
            # If there are no user written files, then the project generation will fail.
            # This is generally expected to occur when generating the project
            # files for an entire folder that contains generated libraries.  User
            # preference is to have these generated libraries skipped and to generate
            # the solution only with projects that have actual user written code.
            # Note that this behavior is consistent with the behavior for projects 
            # that use features where IDE generation is not supported.
            waf_project = Project(project)
            project_contains_user_written_files = waf_project.HasUserWrittenFiles()
            if not project_contains_user_written_files:
                continue

            # EACH SUPPORTED LANGUAGE USES A DIFFERENT FILE FORMAT.
            is_cpp = ('cxx' in project.features)
            if is_cpp:
                # GENERATE THE PROJECT FILE.
                self.GenerateProjectFile(template_env, project)

                # TRACK THE SOLUTION DIRECTORIES.
                workspace_dirs.add(self.GetOutputDir(project))
            else:
                continue

        # AVOID OPENING AN EXCESSIVE NUMBER OF WORKSPACES.
        # Check if the workspaces should be opened.
        if Options.options.open:
            # Prevent opening too many instances of Code::Blocks at once if the user didn't specify targets.
            workspaces_to_open_count = len(workspace_dirs)
            WORKSPACES_TO_OPEN_MAX = 5
            opening_too_many_workspaces = (workspaces_to_open_count > WORKSPACES_TO_OPEN_MAX) and (not Options.options.targets)
            if opening_too_many_workspaces:
                # The user likely forgot to specify a target on the command line.
                error_message = 'Too many workspaces to open: {0}. Did you forget the --targets parameter?'.format(workspaces_to_open_count)
                raise Errors.WafError(error_message)

        # GENERATE THE CODE BLOCKS WORKSPACE FILES.
        for workspace_dir in workspace_dirs:
            workspace_filepath = self.GenerateWorkspaceFile(template_env, workspace_dir)

            # Check if the workspace should be opened.
            if Options.options.open:
                OpenFileInDefaultProgram(workspace_filepath)


    # Generates a project file.
    def GenerateProjectFile(self, template_env, waf_project):
        # LOAD THE PROJECT TEMPLATE.
        project_template = template_env.get_template(
            'CodeBlocks.cbp.template')

        # GENERATE THE PROJECT FILE.
        project = CppProject(waf_project)
        virtual_dir = FileExplorer(project)
        project_text = project_template.render(
            project = project,
            virtual_dir = virtual_dir,
            python_exe_path = sys.executable,
            waf_script_path = GetWafScriptFilepath())

        # STORE THE PROJECT FILE.
        project_file_name = project.GetName() + '.cbp'
        project_file = self.GetOutputDir(waf_project).make_node(project_file_name)
        project_file.write(project_text.encode('utf-8'))

    # Generates a workspace file containing all projects in the given directory.
    def GenerateWorkspaceFile(self, template_env, workspace_dir):
        # GATHER THE C++ PROJECTS.
        project_files = workspace_dir.ant_glob('*.cbp')
        if not project_files:
            return

        # GENERATE THE C++ SOLUTION FILE.
        workspace_template = template_env.get_template(
            'CodeBlocks.workspace.template')
        workspace_text = workspace_template.render(
            workspace_name = workspace_dir.name,
            project_files = project_files)
        workspace_name = workspace_dir.parent.name + '.workspace'
        workspace_file = workspace_dir.make_node(workspace_name)
        workspace_file.write(workspace_text.encode('utf-8'))

        return workspace_file.abspath()

    # Returns the directory where IDE projects files are stored.
    def GetOutputDir(self, waf_project):
        output_dir = waf_project.path.get_bld().make_node('CodeBlocks')
        output_dir.mkdir()
        return output_dir
