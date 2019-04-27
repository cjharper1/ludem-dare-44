from __future__ import absolute_import, division, print_function

from waflib import Errors

from Waf.Utilities import UuidMd5Hash

## \package Waf.IdeIntegration.Project
## This package defines an common interface for task generators that represent a type of build
## project.

## Provides an interface for binding a Waf project to generic project.
class Project(object):
    # Provides binding for the given Waf project.
    def __init__(self, waf_project):
        self.waf_project = waf_project
        pass

    # Returns the name of the project.
    def GetName(self):
        return self.waf_project.name

    # Returns an identifier that is unique across all Waf projects.
    def GetUuid(self):
        unique_id_text = UuidMd5Hash(self.GetName())
        return unique_id_text

    # Returns the directory where build outputs are stored.
    def GetOutputDir(self):
        project_build_dir = self.waf_project.path.get_bld()
        return project_build_dir

    # Returns the project's build varaint. Each variant is stored in a different
    # output directory.
    def GetBuildVariant(self):
        build_variant = self.waf_project.bld.variant
        return build_variant

    # The source directory is the parent directory shared by all source files.
    def GetSourceDir(self, source_files):
        # CHECK IF THE SOURCE DIRECTORY HAS ALREADY BEEN CALCULATED.
        # The calculation is cached in memory to improve performance. The calculation is expensive
        # and many components use the source directory. When cached, project file generation is up
        # to three times faster.
        has_source_dir = hasattr(self.waf_project, 'source_dir')
        if has_source_dir:
            return self.waf_project.source_dir

        # EXCLUDE GENERATED FILES.
        build_dir = self.waf_project.bld.bldnode
        user_written_files = [
            source_file for source_file in source_files
            if not source_file.is_child_of(build_dir)]

        # DEFAULT TO THE PROJECT DIRECTORY.
        if not user_written_files:
            error_msg = (
                'Project has no user written files: ' +
                self.waf_project.name)
            raise Errors.WafError(error_msg)

        # CALCULATE THE SOURCE DIRECTORY.
        source_dir = None
        parent_dir = user_written_files[0].parent
        while parent_dir:
            # CHECK IF THE SOURCE DIRECTORY HAS BEEN FOUND.
            source_dir_found = all([
                source_file.is_child_of(parent_dir)
                for source_file in user_written_files])
            if source_dir_found:
                source_dir = parent_dir
                break

            # TRY THE NEXT PARENT DIRECTORY.
            parent_dir = parent_dir.parent

        # CACHE THE SOURCE DIRECTORY.
        assert source_dir, "Could not find source directory for: %s" % self.GetName()
        self.waf_project.source_dir = source_dir

        # RETURN THE SOURCE DIRECTORY.
        return source_dir
        
    ## Checks if the project contains any user written files.
    ## \return  True if the project contains at least one user written file.
    ##      False if it does not contain any user written files.
    def HasUserWrittenFiles(self):
        # CHECK THE PROJECT SOURCE ATTRIBUTE FOR USER WRITTEN FILES.
        # Files that are generated are always in the build directory, so
        # if the file is not in the build directory it was written by the user.
        build_dir = self.waf_project.bld.bldnode
        for source_file in self.waf_project.source:
            source_file_in_build_directory = source_file.is_child_of(build_dir)
            if not source_file_in_build_directory:
                return True
        
        # CHECK THE PROJECT CATEGORIZED SOURCE ATTRIBUTES FOR USER WRITTEN FILES.
        # For .NET projects the source files are categorized into compiled files, content files,
        # and user control files.  User control files are just a subset of the content files so
        # there is no need to check the files in that category since they have already been checked.
        # Check the compiled files attribute.
        compiled_files_categorized = hasattr(self.waf_project, 'compiled_files')
        if compiled_files_categorized:
            for source_file in self.waf_project.compiled_files:
                source_file_in_build_directory = source_file.is_child_of(build_dir)
                if not source_file_in_build_directory:
                    return True
                    
        # Check the content files attribute.
        content_files_categorized = hasattr(self.waf_project, 'content_files')
        if content_files_categorized:
            for source_file in self.waf_project.content_files:
                source_file_in_build_directory = source_file.is_child_of(build_dir)
                if not source_file_in_build_directory:
                    return True
                    
        # NO USER WRITTEN FILES WERE FOUND.
        return False
