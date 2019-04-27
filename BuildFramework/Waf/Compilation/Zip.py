from __future__ import absolute_import, division, print_function

import os
from zipfile import ZipFile

from waflib import Task
from waflib.Configure import conf
from waflib.Errors import WafError
from waflib.TaskGen import after_method
from waflib.TaskGen import before_method
from waflib.TaskGen import feature

## \package Waf.Compilation.Zip
## This package provides an interface for creating zip files.
## The following examples show how to create a zip file using source
## files, source directories, or a combination of the two. The preserve_directory_structure
## option will place files in folders of the zip archive using the source directory as the root.
## This option only applies to specified directories. Any specified individual files will
## always be placed in the root of the zip archive.
## Example:
## Examine the following directory structure.
## Data
## |---source_dir
##     |----folder1
##     |----folder2
##     |    |------example1.txt
##     |    |------example2.txt
##     |----folder3
##          |------example3.txt
##
## Zipping source_dir here with the preserve_directory_structure option 
## set to True would produce the following zip file.
## folder1
## folder2
## |-----example1.txt
## |-----example2.txt
## folder3
## |-----example3.txt
## \code
##   # CREATE THE ZIP FILE USING SOURCE FILES.
##   bld.zip(
##       source_files = ['ExampleFile1.txt', 'ExampleFile2.txt'],
##       target = 'zookeeper.zip',
##       name = 'ZookeeperDockerPackage',
##       dynamic_source_files = 'Zookeeper_Docker',
##       install_path = bld.env.INSTALLER_INSTALL_PATH)
##
##  # CREATE THE ZIP FILE USING SOURCE DIRECTORIES.
##  bld.zip(
##      source_dirs = build.path,
##      target = 'target.zip',
##      name = 'ExampleZip',
##      preserve_directory_structure = True)
##
##  # CREATE THE ZIP FILE USING SOURCE FILES AND SOURCE DIRECTORIES.
##  bld.zip(
##      source_dirs = build.path,
##      source_files = ['ExampleFile1.txt', 'ExampleFile2.txt'],
##      name = 'ExampleZipFilesAndDirectories',
##      target = 'target.zip'
##      preserve_directory_structure = True)
## \endcode

## Sets the 'zip' alias so that the user can create zip files using the bld.zip interface.
## The features are set to Zip.
@conf
def zip(bld, *k, **kw):
    kw['features'] = ['Zip']
    return bld(*k, **kw)
    
## Configures waf to use the zip command.
def configure(conf):
    # FIND THE ZIP COMMAND AND SAVE ITS LOCATION IN THE CACHE.
    conf.find_program('zip', var = 'ZIP', mandatory = False)
      
## Sets the command for creating zip files.
## \param[in,out] project - The zip file project.
@feature('Zip')
@after_method('ResolveDynamicAttributes')
@before_method('process_rule')
@before_method('process_source')
def CreateZipFile(project):
    # DETERMINE IF EITHER SOURCE FILES OR SOURCE DIR WERE SPECIFIED.
    source_files_supplied = hasattr(project, 'source_files')
    source_dirs_supplied = hasattr(project, 'source_dirs')
    if not (source_files_supplied or source_dirs_supplied):
        error_msg = 'Please specify source files and/or source dirs to zip: ' + project.name
        raise WafError(error_msg)
        
    # DETERMINE IF TARGET WAS SPECIFIED.
    project.zip_filename = getattr(project, 'target', None)
    if not project.zip_filename:
        error_msg = 'Please specify the filepath of the zip file to create: ' + project.name
        raise WafError(error_msg)
        
    # RETRIEVE THE NECESSARY PARAMETERS FOR THIS TASK.
    if source_dirs_supplied:
        # GET THE SUPPLIED SOURCE DIRECTORY.
        project.source_dirs = project.to_nodes(project.source_dirs)
    else:
        # NO DIRECTORIES WERE SUPPLIED TO WRITE.
        project.source_dirs = []
        
    if source_files_supplied:
        # GET THE SUPPLIED SOURCE FILES.
        project.source_files = project.to_nodes(project.source_files)
    else:
        # NO FILES WERE SUPPLIED TO WRITE.
        project.source_files = []
        
    # DETERMINE IF FOLDER STRUCTURE SHOULD BE PRESERVED IN THE ZIP FILE.
    project.preserve_directory_structure = getattr(project, 'preserve_directory_structure', False)
    
    # CREATE THE ZIP BUILD TASK.
    output_node = project.path.get_bld().find_or_declare(project.zip_filename)
    project.zip_build_task = project.create_task('ZipBuildTask', project.source_files, output_node)
    
    # CREATE THE INSTALL TASK.
    InstallZipFile(project)
    
## Generates a task that copies the created zip file to the installation directory.
## The task is only run when installation is performed.
## \param[in,out] project - The project's installation path is given by the
## install_path attribute. If a path is not specified, the bin directory is
## used. The installation task is added to the install_task attribute.
def InstallZipFile(project):
    # GET THE INSTALLATION PATH.
    default_install_path = "${BINARY_INSTALL_PATH}"
    install_path = getattr(project, 'install_path', default_install_path)
    
    # DEFINE THE FILES TO INSTALL.
    install_files = project.zip_build_task.outputs

    # INSTALL THE ZIP FILE.
    project.install_task = project.add_install_files(
        install_to = install_path,
        install_from = install_files,
        env = project.env)
    
## Creates and executes the commands for creating a zip file.
class ZipBuildTask(Task.Task):
    ## Executes the zip command. The compilation produces a zip file in the project's build directory.
    def run(self):
        waf_project = self.generator
        # GET ALL THE FILES THAT NEED TO BE ZIPPED.   
        files_to_zip = [source_file.abspath() for source_file in waf_project.source_files]
        
        # OPEN A ZIP ARCHIVE AT THE TARGET LOCATION.
        zip_filepath = os.path.join(waf_project.path.get_bld().abspath(), waf_project.zip_filename)
        with ZipFile(zip_filepath, 'w') as target_zip_file:
        
            # WRITE ANY SPECIFIED FILES TO THE ZIP ARCHIVE.
            for absolute_filepath in files_to_zip:
                # Strip the folder structure from the filepath.
                filename_index = 1
                (filepath, filename) = os.path.split(absolute_filepath)
                
                # Add the file, specifying that the file should be placed in
                # the root of the zip archive.
                target_zip_file.write(absolute_filepath, filename)
                   
            # WRITE ANY SPECIFIED DIRECTORIES TO THE ZIP ARCHIVE.
            for source_directory_node in waf_project.source_dirs:
                # Get all files in this directory.
                files_in_directory = source_directory_node.ant_glob('**/*')
                for file in files_in_directory:
                    # Get the path to this file.
                    absolute_filepath = file.abspath()
                    
                    # Python will attempt to write the working zip file to itself
                    # if not stopped. This causes an infinite loop. Ensure the zip
                    # file is not being written to itself.
                    if absolute_filepath in zip_filepath:
                        # Skip writing this file.
                        continue
                        
                    # WRITE THE CURRENT FILE DEPENDING ON CONFIGURATION SETTINGS.
                    if waf_project.preserve_directory_structure:
                        # The files will be written to the archive while preserving folder structure
                        # in relation to this directory.
                        source_directory_path = source_directory_node.abspath()
                        filepath_relative_to_source_directory = os.path.relpath(absolute_filepath, source_directory_path)
                        target_zip_file.write(absolute_filepath, filepath_relative_to_source_directory)
                    else:
                        # Strip the folder structure from the filepath.
                        (filepath, filename) = os.path.split(absolute_filepath)
                        
                        # Add the file, specifying that the file should be placed in
                        # the root of the zip archive.
                        target_zip_file.write(absolute_filepath, filename)
        
    ## A human readable summary of the compilation task.
    def __str__(self):
        build_dir = self.generator.bld.path
        summary_text = '{task_type}: {project_name} at {project_dir}'.format(
            task_type = self.__class__.__name__,
            project_name = self.generator.name,
            project_dir = self.generator.path.path_from(build_dir))
        return summary_text
