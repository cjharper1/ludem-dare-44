from __future__ import absolute_import, division, print_function

from collections import namedtuple

from waflib import Utils

from Waf.IdeIntegration.Project import Project

## \package Waf.IdeIntegration.DotNetProject
## This package defines an interface for task generators that represent a .NET project.

## Provides an interface for binding a Waf project to an MS build project
## template.
class DotNetProject(Project):
    # Provides binding for the given Waf project.
    def __init__(self, waf_project):
        super(DotNetProject, self).__init__(waf_project)

    # Returns the directory where build outputs are stored. .NET projects are
    # output to a sub directory with the same name to avoid conflicts between
    # referenced DLLs and MS build temporary files.
    def GetOutputDir(self):
        project_build_dir = self.waf_project.path.get_bld().make_node(
            self.waf_project.name)
        return project_build_dir

    # Returns the binary output name.
    def GetOutputName(self):
        output_name = getattr(
            self.waf_project, 'binary_name', self.waf_project.name)
        return output_name

    # Gets the file extension of the binary output.
    def GetOutputFileExtension(self):
        return {
            'dll' : 'dll',
            'exe' : 'exe',
            'winexe' : 'exe'
        }[self.waf_project.binary_type]
        
    # Returns the binary output type (Library or Exe).
    def GetOutputType(self):
        return {
            'dll' : 'Library',
            'exe' : 'Exe',
            'winexe': 'WinExe'
        }[self.waf_project.binary_type]
        
    # Returns the CPU platform (i.e x64).
    def GetPlatform(self):
        return self.waf_project.env.CPU

    # Returns all defined constants.
    def GetDefinedConstants(self):
        defined_constants = Utils.to_list(getattr(self.waf_project, 'defines', []))
        return defined_constants

    ## Returns all referenced managed binaries.
    ## \return A list of referenced managed binaries.
    def GetReferencedManagedBinaries(self):
        return self.waf_project.referenced_managed_binaries
        
    ## Returns all referenced unmanaged binaries.
    ## \return A list of referenced unmanaged binaries.
    def GetReferencedUnmanagedBinaries(self):
        return self.waf_project.referenced_unmanaged_binaries

    # Returns all referenced .NET system DLLs.
    def GetReferencedSystemDlls(self):
        return self.waf_project.referenced_system_dlls

    # Information about a compiled file. The information is used by the Visual Studio project
    # file. The tuple contains the following objects:
    #   Path - this is the absolute path of the file.
    #   LinkPath - the name of the file to which the compiled file is linked.
    #   Visible - boolean indicating whether the file should be visible in the project.
    #   DependentUponFile - if the compiled file is a code behind or a designer file,
    #     then this would be the filename on which the compiled file depends. Otherwise this is empty.
    #   SubType - the subtype of the file.
    CompiledFileInfo = namedtuple('CompiledFileInfo', ['Path', 'LinkPath', 'Visible', 'DependentUponFile', 'SubType'])

    # Returns all compiled files in a list of tuples. The tuples contain
    # information about each compiled file as defined by a namedtuple in this class.
    def GetCompiledFiles(self):
        # GO THROUGH EACH COMPILED FILE TO GATHER INFORMATION ABOUT THE FILE.
        compiled_file_tuples = []
        for compiled_file in self.waf_project.compiled_files:
            # CHECK WHAT KIND OF FILE THIS IS.
            # A compiled file may be a code behind or a designer file. Both kinds depend upon a user control file.
            # Some checks must be done here in order to make that associataion when creating the project file.
            file_name = compiled_file.name
            is_code_behind = ('.ascx.cs' in file_name) or ('.aspx.cs' in file_name) or ('.asax.cs' in file_name)
            is_designer_file = ('.ascx.designer.cs' in file_name) or ('.aspx.designer.cs' in file_name)

            # CHECK WHETHER THIS IS A CODE BEHIND FILE.
            if is_code_behind:
                # Since this is a code behind file the name of the user control file that it depends
                # on is assumed to have the same filename, but without the '.cs' extension.
                dependent_upon_file = compiled_file.name[:-3]
                subType = 'ASPXCodeBehind'

            # CHECK WHETHER THIS IS A DESIGNER FILE.
            elif is_designer_file:
                # Since this is a designer file the name of the user control file that it depends
                # on is assumed to have the same filename, but without the '.designer.cs' extension.
                dependent_upon_file = compiled_file.name[:-12]
                subType = ''

            else:
                # This is just a regular code file so there is no dependent file.
                dependent_upon_file = ''
                subType = ''

            # GATHER THE INFORMATION ABOUT THE COMPILED FILE.
            compiled_file_information = self.CompiledFileInfo(
                Path = compiled_file.abspath(),
                LinkPath = compiled_file.path_from(self.GetSourceDir()),
                Visible = not compiled_file.is_child_of(self.waf_project.bld.bldnode),
                DependentUponFile = dependent_upon_file,
                SubType = subType)
            compiled_file_tuples.append(compiled_file_information)

        return compiled_file_tuples

    # Returns all content files.
    def GetContentFiles(self):
        return self.waf_project.content_files

    # Returns all embedded resources.
    def GetEmbeddedResources(self):
        return self.waf_project.embedded_resources

    # Gets the application manifest.
    # The original purpose of this feature was to prevent certain applications from being monitored
    # by Program Compatibility Assistant through the inclusion of a manifest file.
    def GetApplicationManifest(self):
        # RETRIEVE THE APPLICATION MANIFEST.
        # Get the content files, the application manifest should be included in the content files.
        content_files = self.GetContentFiles()

        # Look through the content files for the manifest file (file that ends with .manifest),
        # if no manifest file is found then None is returned to indicate that no manifest is available.
        application_manifest =  None
        ManifestFileExtension = ".manifest"
        for content_file in content_files:
            # Check if we've found the manifest file.
            manifest_file_found = content_file.abspath().endswith(ManifestFileExtension)
            if manifest_file_found:
                # We found the manifest file, so stop the search.
                application_manifest = content_file
                break

        return application_manifest

    # The source directory is the parent directory shared by all source files.
    def GetSourceDir(self):
        # GET THE LIST OF SOURCE FILES.
        is_categorized = hasattr(self.waf_project, 'compiled_files')
        if is_categorized:
            # Use the list of categorized files.
            source_files = self.waf_project.compiled_files
        else:
            # Use the original source files.
            source_files = self.waf_project.source

        # RETURN THE SOURCE DIRECTORY.
        source_dir = super(DotNetProject, self).GetSourceDir(source_files)
        return source_dir
