from __future__ import absolute_import, division, print_function

import glob
import os

from Waf.IdeIntegration.DotNetProject import DotNetProject

## \package Waf.IdeIntegration.AspDotNetProject
## This package defines an interface for task generators that represent an ASP.NET web project.

## Provides an interface for binding a Waf project to an ASP.NET Microsoft
## build project template.
class AspDotNetProject(DotNetProject):
    # Provides binding for the given Waf project.
    def __init__(self, waf_project):
        super(AspDotNetProject, self).__init__(waf_project)

    # The configuration file to use.
    def GetWebConfig(self):
        project_dir = self.waf_project.path
        web_config = project_dir.make_node(self.waf_project.web_config)
        return web_config

    # The site map to use.
    def GetWebSitemap(self):
        project_dir = self.waf_project.path
        web_sitemap = project_dir.make_node(self.waf_project.web_sitemap)
        return web_sitemap

    # The directory where the compiled website is stored.
    def GetWebStagingDir(self):
        web_staging_name = 'WebStaging'
        web_staging_dir = self.GetOutputDir().make_node(web_staging_name)
        return web_staging_dir

    # Whether or not Jasob Obfuscation is enabled for use.
    def IsJasobObfuscationEnabled(self):
        # Check to see if the Web project has a Jasob configuration file specified.
        has_jasob_config = hasattr(self.waf_project, 'jasob_config')
        if not has_jasob_config:
            return False

        # Check to see if obfuscation is enabled.
        jasob_obfuscation_enabled = (
            self.waf_project.env.OBFUSCATE and
            self.waf_project.env.JASOB)
        return jasob_obfuscation_enabled

    # Get the path to the pre-compilation Jasob settings file.
    def GetPreCompilationJasobSettingsFilepath(self):
        # GET THE PATH TO THE PRE-COMPILATION JASOB SETTINGS FILE.
        # Create the path to the pre-compilation Jasob settings file by getting the name of the source Jasob web settings file
        # and putting it in the pre-compilation web source directory.
        pre_compilation_web_source_directory = self.GetWebStagingDir().parent.make_node('WebSource').abspath()
        jasob_source_config_path = self.waf_project.path.make_node(self.waf_project.jasob_config).abspath()
        pre_compilation_jasob_config_filepath = os.path.join(pre_compilation_web_source_directory, os.path.basename(jasob_source_config_path))

        return pre_compilation_jasob_config_filepath

    # Whether or not to keep sensitive terms in the project.
    def KeepSensitiveTerms(self):
        # Check if the user has specified whether or not they would like Jasob to keep sensitive terms.
        # For safety by default we will assume that they want to remove sensitive terms.
        DEFAULT_REMOVE_SENSITIVE_TERMS_IF_NOT_PRESENT = False
        jasob_keep_sensitive_terms = getattr(self.waf_project, 'jasob_keep_sensitive_terms', DEFAULT_REMOVE_SENSITIVE_TERMS_IF_NOT_PRESENT)
        return jasob_keep_sensitive_terms

    # The command used to obfuscate the Web site.
    def GetObfuscationCommand(self):
        # Form the command to perform Web site obfuscation.
        jasob_executable = ''.join(self.waf_project.env.JASOB)
        # NOTE: We use the WebSource folder as both the source and the destination folder. This is because we may need to do some preprocessing on the
        # files before Jasob runs and we don't want to make those changes to the actual source files so we make the changes to the files in WebSource.
        pre_compilation_web_source_directory = self.GetWebStagingDir().parent.make_node('WebSource').abspath()
        jasob_source_config_path = self.waf_project.path.make_node(self.waf_project.jasob_config).abspath()
        # This is the jasob config file whose paths have been updated to reflect the file locations in the web source folder.
        pre_compilation_jasob_config_filepath = self.GetPreCompilationJasobSettingsFilepath()
        # The parameters for the Jasob obfuscation command are explained below.
        # src: The website folder or a Jasob project file you wish to obfuscate.
        # wss: If you are obfuscating a website, this parameter specifies the web site settings file to use for
        # obfuscation.
        # destfolder: The folder to place the obfuscated website or project.
        # nomarkall: Tells Jasob not to default mark names for obfuscation. Without this option Jasob will
        # automatically obfuscate any names that it discovers that are not in the website settings or project file.
        # cpuusage: Tells Jasob how much CPU time it is allowed to consume.  0 indicates 100% of the CPU usage.
        # nosp: Stops the progress dialog from displaying.
        obfuscation_command = '"{0}" /src:"{1}" /wss:"{2}" /destfolder:"{3}" /nomarkall /cpuusage:0 /nosp'.format(
            jasob_executable,
            pre_compilation_web_source_directory,
            pre_compilation_jasob_config_filepath,
            pre_compilation_web_source_directory)

        # Substitute the quotes used above for XML-compatible quotes.
        obfuscation_command = obfuscation_command.replace('"', '&quot;')
        return obfuscation_command

    # Returns the command to keep sensitive terms in a file when Jasob is run. This means that all instances of JasobNoObfs remove=true
    # will be removed.
    # param[in] filepath - The path of the file you want to keep sensitive terms in.
    def GetKeepSensitiveTermsCommand(self, filepath):
        source_directory = self.GetSourceDir().abspath()
        pre_compilation_web_source_directory = self.GetWebStagingDir().parent.make_node('WebSource').abspath()
        # We get the path of the file in the pre-compilation directory by replacing the portion of the filepath that places the file
        # in the source directory with the path to the pre-compilation directory.
        # ex: E:\Data\WebSite\Scripts\SomeFile.js -> E:\Data\build\SomeVariant\WebSource\Scripts\SomeFile.js.
        # Where E:\Data\WebSite is the source directory and E:\Data\build\SomeVariant\WebSource is the pre-compilation source
        # directory.
        pre_compilation_web_source_filepath = filepath.replace(source_directory, pre_compilation_web_source_directory)

        # CREATE COMMAND FOR KEEPING SENSITIVE TERMS.
        # This replaces JasobNoObfs elements from a given file. It runs sed on the original source file, but saves the file
        # to the pre-compilation directory.
        keep_sensitive_terms_command = 'sed -e "s/^.*JasobNoObfs.*$//g" "{0}" > "{1}"'.format(filepath, pre_compilation_web_source_filepath)
        # Substitute the quotes used above for XML-compatible quotes.
        keep_sensitive_terms_command = keep_sensitive_terms_command.replace('"', '&quot;')
        return keep_sensitive_terms_command

    # Retrieves all of the JavaScript filepaths in the source directory.
    def GetAllJavaScriptFilepathsInSourceDirectory(self):
        source_directory = self.GetSourceDir().abspath()
        source_javascript_filepaths = glob.glob(os.path.join(source_directory, "**/*.js"))
        return source_javascript_filepaths

    # Gets the command for copying over the Jasob config file and updating the file paths for its new location.
    def GetCopyJasobWebsiteSettingFileCommand(self):
        pre_compilation_web_source_directory_path = self.GetWebStagingDir().parent.make_node('WebSource').abspath()
        jasob_config_path = self.waf_project.path.make_node(self.waf_project.jasob_config).abspath()

        # BUILD THE COMMAND TO UPDATE THE PATHS IN THE JASOB CONFIG FILE.
        # It is expected that the jasob config filepaths will be of the form Web\{PathToFile}. We're just removing Web\ because logically
        # we're moving the Jasob configuration file down one folder. We want to match the Web/ at the beginning of the path so we match the quotation
        # mark at the beginning of the path in the settings file. The caret (^) is the escape symbol in the Windows shell, but does not work
        # inside of quoted strings, so you have to break the command up around the quotation marks that need escaping.
        copy_jasob_website_settings_command = 'sed -e "s/"^""Web\\\\/"^""/g" "{0}" > "{1}"'.format(jasob_config_path, os.path.join(pre_compilation_web_source_directory_path, os.path.basename(jasob_config_path)))
        # Substitute the quotes used above for XML-compatible quotes.
        copy_jasob_website_settings_command = copy_jasob_website_settings_command.replace('"', '&quot;')
        return copy_jasob_website_settings_command

    # All of the referenced projects used to build this project.
    def GetReferencedProjects(self):
        project_names = [project.name for project in self.waf_project.referenced_projects]
        return project_names

    # Returns the source directory of all the referenced ASP.NET library projects.
    def GetAspDotNetReferencedSourceDirs(self):
        # GO THROUGH EACH REFERENCED PROJECT TO GET THE SOURCE DIRECTORIES FOR THE REFERENCED ASP.NET LIBRARIES.
        reference_projects_source_dirs = []
        for referenced_project in self.waf_project.referenced_projects:
            # Check whether the referenced project is an ASP.NET library.
            is_asp_net_library = 'asp_net_library' in referenced_project.features
            if is_asp_net_library:
                # Get the source directory for the referenced project.
                dot_net_binding = DotNetProject(referenced_project)
                reference_projects_source_dirs.append(dot_net_binding.GetSourceDir())

        return reference_projects_source_dirs
