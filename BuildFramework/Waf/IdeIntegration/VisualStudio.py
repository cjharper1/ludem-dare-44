from __future__ import absolute_import, division, print_function

from collections import namedtuple
import itertools
import os
import sys

from jinja2 import Environment, FileSystemLoader
from waflib import Errors
from waflib import Options
from waflib import Utils
from waflib.Build import BuildContext

from Waf.IdeIntegration.AspDotNetProject import AspDotNetProject
from Waf.IdeIntegration.CppProject import CppProject
from Waf.IdeIntegration.DotNetProject import DotNetProject
from Waf.IdeIntegration.FileExplorer import FileExplorer
from Waf.IdeIntegration.Project import Project
from Waf.Utilities import GetTargetProjects
from Waf.Utilities import GetWafScriptFilepath
from Waf.Utilities import OpenFileInDefaultProgram
from Waf.Utilities import UuidMd5Hash

## \package Waf.IdeIntegration.VisualStudio
## This package defines a command for generating project files for the Visual Studio IDE.

## This command generates C++, .NET, or ASP.NET project files for the Visual Studio IDE.
class VisualStudioContext(BuildContext):
    # The comment below provides the help text for the command-line.
    '''generates a visual studio solution'''
    cmd = 'msvs'
    fun = 'build'

    # Generates Visual Studio projects and solutions. The method disables the
    # actual build.
    def execute_build(self):
        # LOAD THE TEMPLATE ENVIRONMENT.
        template_dir = self.path.find_node(
            'BuildFramework/Waf/IdeIntegration')
        template_loader = FileSystemLoader(template_dir.abspath())
        template_env = Environment(
            loader = template_loader,
            trim_blocks = True,
            lstrip_blocks = True)

        # PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        projects = GetTargetProjects(self)

        # GENERATE VISUAL STUDIO PROJECT FILES.
        solution_dirs = set([])
        solution_filepaths = set([])
        for waf_project in projects:
            # LOAD THE PROJECT.
            waf_project.post()
            
            # MAKE SURE THE PROJECT HAS USER WRITTEN FILES.
            # If there are no user written files, then the project generation will fail.
            # This is generally expected to occur when generating the Visual Studio
            # solution for an entire folder that contains generated libraries.  User
            # preference is to have these generated libraries skipped and to generate
            # the solution only with projects that have actual user written code.
            # Note that this behavior is consistent with the behavior for projects 
            # that use features where IDE generation is not supported.
            project = Project(waf_project)
            project_contains_user_written_files = project.HasUserWrittenFiles()
            if not project_contains_user_written_files:
                continue
            
            # EACH SUPPORTED LANGUAGE USES A DIFFERENT FILE FORMAT.
            is_cpp = ('cxx' in waf_project.features)
            is_dot_net = ('dot_net' in waf_project.features)
            is_asp_net_website = ('asp_net_website' in waf_project.features)
            is_asp_net_library = ('asp_net_library' in waf_project.features)
            if is_cpp:
                # GENERATE THE PROJECT FILE.
                self.GenerateCppProjectFile(template_env, waf_project)

                # GENERATE THE FILTER FILE.
                self.GenerateCppFilterFile(template_env, waf_project)

                # TRACK THE SOLUTION DIRECTORIES.
                solution_dirs.add(self.GetOutputDir(waf_project))

            elif is_dot_net:
                # GENERATE THE PROJECT FILE.
                self.GenerateDotNetProjectFile(template_env, waf_project)

                # TRACK THE SOLUTION DIRECTORIES.
                solution_dirs.add(self.GetOutputDir(waf_project))

            elif is_asp_net_library:
                # GENERATE THE PROJECT FILE.
                self.GenerateWebApplicationProjectFile(template_env, waf_project)

                # TRACK THE SOLUTION DIRECTORIES.
                solution_dirs.add(self.GetOutputDir(waf_project))

            elif is_asp_net_website:
                # GENERATE THE WEB SOLUTION.
                solution_filepaths.add(self.GenerateWebSolutionFile(template_env, waf_project))

                # GENERATE THE WEB PROJECT FILE.
                self.GenerateWebProjectFile(template_env, waf_project)

            else:
                continue

        # GENERATE THE VISUAL STUDIO SOLUTION FILES.
        for solution_dir in solution_dirs:
            solution_filepaths.add(self.GenerateSolutionFile(template_env, solution_dir))

        # OPEN THE VISUAL STUDIO PROJECT FILES.
        for solution_filepath in solution_filepaths:
            OpenFileInDefaultProgram(solution_filepath)

    # Generates a MSVC++ project file.
    def GenerateCppProjectFile(self, template_env, waf_project):
        # LOAD THE PROJECT TEMPLATE.
        project_template = template_env.get_template(
            'VisualStudio.vcxproj.template')

        # GENERATE THE PROJECT FILE.
        project = CppProject(waf_project)
        project_text = project_template.render(
            project = project,            
            python_exe_path = sys.executable,
            waf_script_path = GetWafScriptFilepath())

        # STORE THE PROJECT FILE.
        project_file_name = project.GetName() + '.vcxproj'
        project_file = self.GetOutputDir(waf_project).make_node(project_file_name)
        project_file.write(project_text.encode('utf-8'))

    # Generates a MSVC++ filers file to organize the solution explorer.
    def GenerateCppFilterFile(self, template_env, waf_project):
        # LOAD THE FILTER TEMPLATE.
        filter_template = template_env.get_template(
            'VisualStudio.vcxproj.filters.template')

        # GENERATE THE FILTER FILE.
        project = CppProject(waf_project)
        project_filters = FileExplorer(project)
        filter_text = filter_template.render(
            project = project,
            project_filters = project_filters)

        # STORE THE FILTER FILE.
        filter_file_name = project.GetName() + '.vcxproj.filters'
        filter_file = self.GetOutputDir(waf_project).make_node(filter_file_name)
        filter_file.write(filter_text.encode('utf-8'))

    # Generates a Microsoft .NET project file.
    def GenerateDotNetProjectFile(self, template_env, waf_project):
        # LOAD THE PROJECT TEMPLATE.
        project_template = template_env.get_template('VisualStudio.csproj.template')

        # DETERMINE IF THE PROJECT IS AN NUNIT TEST.
        # If it's an Nunit test, the Nunit GUI should be added to the csproj file
        # to facilitate running tests through the IDE.
        is_nunit_tester = 'nunit_test' in waf_project.features
        nunit_gui_exe = waf_project.env.NUNIT_GUI[0] if waf_project.env.NUNIT_GUI else None

        # GENERATE THE PROJECT FILE.
        project = DotNetProject(waf_project)
        project_text = project_template.render(
            build_dir = waf_project.bld.bldnode,
            project = project,
            nunit_gui_exe = nunit_gui_exe if is_nunit_tester else None,            
            python_exe_path = sys.executable,
            waf_script_path = GetWafScriptFilepath())

        # STORE THE PROJECT FILE.
        project_file_name = project.GetName() + '.csproj'
        project_file = self.GetOutputDir(waf_project).make_node(project_file_name)
        project_file.write(project_text.encode('utf-8'))

    # Generates an ASP.NET web solution file.
    def GenerateWebSolutionFile(self, template_env, waf_project):
        # LOAD THE SOLUTION TEMPLATE.
        solution_template = template_env.get_template(
            'VisualStudio.webproj.sln.template')

        # GENERATE THE SOLUTION FILE.
        project = AspDotNetProject(waf_project)
        solution_text = solution_template.render(project = project)

        # STORE THE SOLUTION FILE.
        solution_file_name = project.GetName() + '.sln'
        solution_file = self.GetOutputDir(waf_project).make_node(solution_file_name)
        solution_file.write(solution_text.encode('utf-8') + '\n')
        return solution_file.abspath()

    # Generates an ASP.NET web project file.
    def GenerateWebProjectFile(self, template_env, waf_project):
        # LOAD THE SOLUTION TEMPLATE.
        project_template = template_env.get_template(
            'VisualStudio.webproj.template')

        # GENERATE THE PROJECT FILE.
        project = AspDotNetProject(waf_project)
        project_text = project_template.render(
            project = project,            
            python_exe_path = sys.executable,
            waf_script_path = GetWafScriptFilepath())

        # STORE THE PROJECT FILE.
        project_file_name = project.GetName() + '.csproj'
        project_file = self.GetOutputDir(waf_project).make_node(project_file_name)
        project_file.write(project_text.encode('utf-8'))

    # Generates an ASP.NET web application project file.
    def GenerateWebApplicationProjectFile(self, template_env, waf_project):
        # LOAD THE SOLUTION TEMPLATE.
        project_template = template_env.get_template(
            'VisualStudio.webAppProj.template')

        # GENERATE THE PROJECT FILE.
        project = DotNetProject(waf_project)
        project_text = project_template.render(
            build_dir = waf_project.bld.bldnode,
            project = project,            
            python_exe_path = sys.executable,
            waf_script_path = GetWafScriptFilepath())

        # STORE THE PROJECT FILE.
        project_file_name = project.GetName() + '.csproj'
        project_file = self.GetOutputDir(waf_project).make_node(project_file_name)
        project_file.write(project_text.encode('utf-8'))

    # Generates a solution file containing all projects in the given directory.
    def GenerateSolutionFile(self, template_env, solution_dir):
        # GATHER THE C++ PROJECTS.
        cpp_project_files = solution_dir.ant_glob('*.vcxproj')
        cpp_projects = self.GatherProjectInfo(cpp_project_files)
        if cpp_projects:
            # GENERATE THE C++ SOLUTION FILE.
            cpp_sln_template = template_env.get_template(
                'VisualStudio.vcxproj.sln.template')
            cpp_sln_text = cpp_sln_template.render(
                projects = cpp_projects,
                build_variant = self.variant)
            cpp_sln_name = solution_dir.parent.name + '.sln'
            cpp_sln_file = solution_dir.make_node(cpp_sln_name)
            cpp_sln_file.write(cpp_sln_text.encode('utf-8') + '\n')

            # Return the filepath.
            return cpp_sln_file.abspath()

        # GATHER THE .NET PROJECTS.
        dot_net_project_files = solution_dir.get_bld().ant_glob('*.csproj')
        dot_net_projects = self.GatherProjectInfo(dot_net_project_files)
        if dot_net_projects:
            # GENERATE THE DOT NET SOLUTION FILE.
            dot_net_sln_template = template_env.get_template(
                'VisualStudio.csproj.sln.template')
            dot_net_sln_text = dot_net_sln_template.render(
                projects = dot_net_projects,
                build_variant = self.variant)
            dot_net_sln_name = solution_dir.parent.name + '.net.sln'
            dot_net_sln_file = solution_dir.make_node(dot_net_sln_name)
            dot_net_sln_file.write(dot_net_sln_text.encode('utf-8') + '\n')

            # Return the filepath.
            return dot_net_sln_file.abspath()

    # Returns basic information about the given projects.
    def GatherProjectInfo(self, project_files):
        # DEFINE THE PROJECT INFO CONTAINER.
        ProjectInfo = namedtuple('ProjectInfo', ['Name', 'Id'])

        # GATHER THE PROJECT INFO.
        projects = []
        for project_file in project_files:
            # BUILD THE PROJECT.
            project_name = os.path.splitext(project_file.name)[0]
            project_id = UuidMd5Hash(project_name)
            project = ProjectInfo(
                Name = project_name,
                Id = project_id)

            # STORE THE PROJECT.
            projects.append(project)

        # RETURN THE PROJECT INFO.
        return projects

    # Returns the directory where IDE projects files are stored.
    def GetOutputDir(self, waf_project):
        output_dir = waf_project.path.get_bld().make_node('VisualStudio')
        output_dir.mkdir()
        return output_dir

