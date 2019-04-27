from __future__ import absolute_import, division, print_function

from collections import namedtuple
import os

from Waf.Utilities import UuidMd5Hash

## \package Waf.IdeIntegration.FileExplorer
## This package defines a class for that represents the virtual directory used to explore files
## within the IDE.

## The virtual root directory used to explore files within the IDE.
class FileExplorer(object):
    ## Defines the virtual directory for the given project.
    def __init__(self, project):
        self.project = project

    ## A virtual directory within the file explorer.
    VirtualDirectory = namedtuple('VirtualDirectory', ['Path', 'Id'])

    ## Returns all virtual sub directories.
    def GetDirs(self):
        # GATHER ALL UNIQUE VIRTUAL DIRECTORIES FOR ALL FILES IN THE PROJECT.
        virtual_dirs = set([])
        code_files = (
            self.project.GetSourceFiles() +
            self.project.GetHeaderFiles())
        for code_file in code_files:
            # ADD THE IMMEDIATE VIRTUAL DIRECTORY FOR THE CURRENT FILE.
            # The immediate virtual directory is added separately from additional parent directories to simplify logic.
            # Since we want to add virtual, not "physical", parent directories, we need at least one virtual path
            # so that obtaining the parent directories will stop at the root virtual parent, not the physical one.
            # The current simplest way to get a virtual path is to get the immediate virtual parent directory for
            # a file.  When doing this, parent directories will be obtained starting above the immediate virtual directory,
            # not the current file, so the immediate virtual directory must be added here to avoid being missed.
            virtual_dir = self.GetVirtualDir(code_file)
            virtual_dirs.add(virtual_dir)

            # ADD VIRTUAL DIRECTORIES FOR EACH PARENT DIRECTORY.
            # Virtual directories for each parent directory need to be added to ensure that filters are properly created
            # for Visual Studio.  Without having virtual directories for each parent, parent directories without any
            # files (only sub-directories) may not have filters, which throws off the file filters in Visual Studio.
            parent_virtual_dir_paths = self.GetParentDirs(virtual_dir.Path)
            for parent_virtual_dir_path in parent_virtual_dir_paths:
                # Add the current virtual parent directory to the unique set.
                parent_virtual_dir = self.CreateVirtualDir(parent_virtual_dir_path)
                virtual_dirs.add(parent_virtual_dir)

        # RETURN UNIQUE VIRTUAL DIRECTORIES.
        return virtual_dirs

    ## The unique ID of the file's virtual sub-directory.
    def GetVirtualDir(self, file, root_virtual_path = None):
        # DETERMINE THE ROOT VIRTUAL DIRECTORY PATH.
        if root_virtual_path is None:
            # Determine the virtual path from the file extension.
            root_virtual_path = self.GetRootVirtualDirPath(file)

        # BUILD THE VIRTUAL DIRECTORY PATH.
        has_sub_dir = (file.parent != self.project.GetSourceDir())
        if has_sub_dir:
            sub_dir = file.parent.path_from(self.project.GetSourceDir())
            virtual_dir_path = os.sep.join([root_virtual_path, sub_dir])
        else:
            virtual_dir_path = root_virtual_path

        # RETURN THE VIRTUAL DIRECTORY.
        return self.CreateVirtualDir(virtual_dir_path)

    ## Creates a virtual directory with a unique ID based on the provided path.
    ## \param[in]   virtual_dir_path - The path to use for the virtual directory.
    ## \return      A virtual directory with the provided path and a unique ID.
    def CreateVirtualDir(self, virtual_dir_path):
        # CALCULATE THE VIRTUAL PATH ID.
        virtual_dir_id = UuidMd5Hash(virtual_dir_path)

        # RETURN THE VIRTUAL DIRECTORY.
        virtual_dir = self.VirtualDirectory(
            Path = virtual_dir_path,
            Id = virtual_dir_id);
        return virtual_dir

    ## Gets the root virtual directory path for a file based on its type.
    ## \param[in]    file - The file in the project to determine the root
    ##               virtual directory path for.
    ## \return       The root virtual directory path for the file.
    def GetRootVirtualDirPath(self, file):
        # The file should go in a different root virtual directory
        # depending on its type.  We want to keep source files and
        # header files separate.
        is_source = ('.cpp' == file.suffix())
        root_virtual_path = 'Sources' if is_source else 'Headers'
        return root_virtual_path

    ## Gets all parent directories of the provided path.  The path may
    ## be relative or absolute, and the returned directories will be
    ## relative or absolute (depending on the type of path provided).
    ## \param[in]   path - The file or folder path (as a string)
    ##              for which to retrieve parent directories.
    ## \return      A set of all parent directories of the provided path.
    def GetParentDirs(self, path):
        parent_dirs = set([])

        # INITIALIZE THE DIRECTORY FOR PROCESSING TO BE THE FIRST PARENT DIRECTORY.
        # When splitting a path, the first item in the returned tuple will be the
        # parent directory of the current path, and the second item will be the
        # item after the last slash in the path.
        current_parent_dir_path, current_dir_name = os.path.split(path)

        # GATHER ALL PARENT DIRECTORY PATHS.
        # When no more parent directories exist, the current path will evaluate to false.
        while current_parent_dir_path:
            # STORE THE CURRENT PARENT DIRECTORY PATH.
            parent_dirs.add(current_parent_dir_path)

            # GET THE NEXT PARENT DIRECTORY.
            current_parent_dir_path, current_dir_name = os.path.split(current_parent_dir_path)

        return parent_dirs
