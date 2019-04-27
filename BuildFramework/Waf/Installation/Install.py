from __future__ import absolute_import, division, print_function

import os
import platform

from waflib import Errors
from waflib import Utils
from waflib import Options
from waflib.TaskGen import feature
from waflib.TaskGen import before_method
from waflib.TaskGen import after_method
from waflib.Tools import cxx

from Waf.Utilities import Platform

## \package Waf.Installation.Install
## This package customizes the Waf install command for our products. The command copies the build to
## a remote directory with a custom structure.

## Configures the installation directory paths in the environment.
## \param[in] conf - The command context is shared by all user defined initialization
## methods.
def configure(conf):
    # BUILD THE ROOT INSTALLATION PATH.
    # The path is relative to the destination directory.
    os_name = 'Windows'
    if Platform.IsLinux():
        # For Linux builds, more specificity is required since there are many supported 
        # distributions and version numbers.
        (linux_distribution_name,distribution_version_number,distribution_version_codename) = platform.linux_distribution()
        os_name = linux_distribution_name + distribution_version_number
    platform_name = os_name + conf.env.CPU

    # Replace spaces with underscores to avoid problems due to spaces in the install path.
    install_root_path = os.path.join(
        'v%s' % conf.env.PRODUCT_VERSION_NUMBER,
        '%s' % platform_name.replace(' ', '_'))

    # OVERRIDE THE BUILT-IN INSTALLATION SUB-DIRECTORIES.
    # The bin and lib directories are defined by the Waf configuration context.
    conf.env.BINDIR = os.path.join(install_root_path, 'bin')
    conf.env.LIBDIR = os.path.join(install_root_path, 'lib')

    # ADD THE INSTALLATION SUB-DIRECTORIES.
    # The additional environment variables are named for consistency.
    conf.env.BINARY_INSTALL_PATH = os.path.join(install_root_path, 'bin')
    conf.env.INSTALLER_INSTALL_PATH = os.path.join(
        install_root_path,
        'install')
    conf.env.UTILITY_INSTALL_PATH = os.path.join(install_root_path, 'util')
    conf.env.INCLUDE_INSTALL_PATH = os.path.join(install_root_path, 'include')

## Initializes waf for running the install command.
## \param[in]   context - The waf context.
def init(context):
    try:
        # DETERMINE WHETHER AN INSTALL COMMAND WAS GIVEN.
        # Also get its index so that we can add a build command
        # at its location.
        # TODO: this is a hack we're adding to guarantee that any dynamically-
        # generated includes are generated before the install command runs, since 
        # there have been problems to date with the includes not necessarily existing
        # before the install command runs.  We should investigate a better way to ensure
        # these includes can be installed regardless of the state of the filesystem prior
        # to running waf.
        INSTALL_COMMAND_NAME = "install"
        install_command_index = Options.commands.index(INSTALL_COMMAND_NAME)
    except ValueError:
        return

    # ADD A BUILD COMMAND BEFORE THE INSTALL COMMAND.
    # Dynamically-generated includes won't exist when the install command 
    # runs unless they are built ahead of time by the build command.
    BUILD_COMMAND_NAME = "build"
    if BUILD_COMMAND_NAME not in Options.commands[:install_command_index]:
        Options.commands.insert(install_command_index, BUILD_COMMAND_NAME)

## Configures the installation directory paths specific to the project's
## environment. Projects are installed to sub-folders with the same name.
@feature('*')
@before_method('process_source')
def ConfigureInstallationDirectory(project):
    # OVERRIDE THE BUILT-IN INSTALLATION SUB-DIRECTORIES.
    # The bin and lib directories are defined by the Waf configuration context.
    # Note that the build variant is being added to the path to allow us to differentiate
    # between build artifacts when running an install command for multiple variants for 
    # the same version of a release.  Without this, one variant's artifacts will overwrite
    # a previous variant's.
    project.env.BINDIR = os.path.join(project.env.BINDIR, project.bld.variant, project.name)
    project.env.LIBDIR = os.path.join(project.env.LIBDIR, project.bld.variant)
    
    # ADD THE INSTALLATION SUB-DIRECTORIES.
    # The additional environment variables are named for consistency.
    print (project.env.BINARY_INSTALL_PATH)
    print (project.bld.variant)
    print (project.name)
    project.env.BINARY_INSTALL_PATH = os.path.join(
        project.env.BINARY_INSTALL_PATH, project.bld.variant, project.name)
    project.env.INSTALLER_INSTALL_PATH = os.path.join(
        project.env.INSTALLER_INSTALL_PATH,
        project.bld.variant,
        project.name)
    project.env.UTILITY_INSTALL_PATH = os.path.join(
        project.env.UTILITY_INSTALL_PATH,
        project.bld.variant, 
        project.name)
    project.env.INCLUDE_INSTALL_PATH = os.path.join(
        project.env.INCLUDE_INSTALL_PATH, 
        project.name)

## Installs all supporting files alongside the project's output.
## \param[in] project - What files to install and where they should go are
##     specified by the install_path and install_files attributes.
@feature('*')
@before_method('process_source')
def InstallSupportingFiles(project):
    # CHECK IF SUPPORT FILES ARE SPECIFIED.
    supporting_files_specified = hasattr(project, 'install_files')
    if not supporting_files_specified:
        return

    # VERIFY THAT AN INSTALLATION PATH IS SPECIFIED.
    # The installation path must be explicitly defined because the default
    # path depends on the type of project. This approach is simpler than
    # handling all subtypes.
    install_path_specified = hasattr(project, 'install_path')
    if not install_path_specified:
        error_msg = ('{project_name} at {project_dir} - An installation path '
            'must be specified for supporting files.').format(
            project_name = project.name,
            project_dir = project.path.path_from(project.bld.srcnode))
        raise Errors.WafError(error_msg)
    
    # INSTALL THE SUPPORTING FILES.
    # The relative_trick argument will preserve the folder hierarchy when installing whole folders.
    install_files = project.to_nodes(project.install_files)
    project.install_task = project.add_install_files(
        install_to = project.install_path,
        install_from = install_files,
        cwd = project.path,
        relative_trick = True,
        env = project.env)

## Installs all include files for the project in the include installation path.
## \param[in] project - the project whose include files are to be installed.  Note that only
##      those projects which specify the install_includes_and_lib attribute will be processed.
@feature('c','cxx')
@before_method('process_source')
def InstallIncludeFiles(project):
    # CHECK IF INCLUDE AND LIBRARY FILES ARE SPECIFIED.
    install_include_files = getattr(project, 'install_includes_and_lib', False)
    exported_includes = getattr(project, 'export_includes', [])
    if not (install_include_files and exported_includes):
        return
        
    # GET THE LIST OF ALL HEADER FILES TO BE INSTALLED.
    header_files = []
    # The exported_includes can be specified as a list or a string.  Make it a list for consistency.
    if not isinstance(exported_includes, list):
        exported_includes = [exported_includes]
    for exported_include in exported_includes:
        header_files.extend(project.path.ant_glob(os.path.join(exported_include, '**/*.h')))
        
    # INSTALL THE INCLUDE FILES.
    # The relative_trick argument will preserve the folder hierarchy when installing whole folders.
    # Note that this functionality requires the headers to be stored in a path following the convention
    # <project_name>/Code/<project_name>.
    project_code_root_folder = os.path.join('Code', project.name)
    project.install_task = project.add_install_files(
        install_to = project.env.INCLUDE_INSTALL_PATH,
        install_from= header_files,
        cwd = project.path.find_node(project_code_root_folder),
        relative_trick = True,
        env = project.env)
    
## Installs all output library files in the lib installation path.
## \param[in] project - the project whose output files are to be installed.  Note that only
##      those projects which specify the install_includes_and_lib attribute will be processed.
@feature('c', 'cxx', 'cxxstlib', 'cxxshlib', 'dot_net')
@after_method('apply_link')
def InstallLibraryFiles(project):
    # CHECK IF INCLUDE AND LIBRARY FILES ARE SPECIFIED.
    install_library_files = getattr(project, 'install_includes_and_lib', False)
    if not install_library_files:
        return

    # INSTALL THE LIBRARY FILES.
    # With relative_trick set to false, all libraries will go into the same folder.
    project_outputs = project.link_task.outputs
    project.install_task = project.add_install_files(
        install_to = project.env.LIBDIR,
        install_from = project_outputs,
        relative_trick = False,
        env = project.env)
        
## Installs all generated header files in the include installation path.
## \param[in] project - the project whose output files are to be installed.  Note that only
##      those projects which specify the install_includes_and_lib attribute will be processed.
@feature('c','cxx', 'cxxstlib', 'cxxshlib')
@after_method('process_rule', 'process_source')
def InstallGeneratedIncludeFiles(project):
    # CHECK IF INCLUDE AND LIBRARY FILES ARE SPECIFIED.
    install_include_files = getattr(project, 'install_includes_and_lib', False)
    exported_includes = getattr(project, 'export_includes', [])
    if not (install_include_files and exported_includes):
        return

    # RETRIEVE THE LIST OF GENERATED HEADER FILES TO BE ADDED TO THE INCLUDES.
    generated_header_files = []
    # The export_includes can be specified as a list or a string.  Make it a list for consistency.
    if not isinstance(exported_includes, list):
        exported_includes=[exported_includes]
    for exported_include in exported_includes:
        # Note that remove = False must be specified in the ant_glob() calls below to prevent
        # the files from being removed, since the default behavior is to remove any files that 
        # do not exist (and generated files are typically generated after this function is run).
        generated_header_files.extend(project.path.get_bld().ant_glob(os.path.join(exported_include, '**/*.h'), remove = False))
   
    LIST_EMPTY_COUNT = 0
    generated_headers_present =  (len(generated_header_files) != LIST_EMPTY_COUNT)
    if (generated_headers_present):
        # INSTALL THE DYNAMICALLY-GENERATED INCLUDES.
        # Note that this functionality requires the headers to be stored in a path following the convention
        # <project_name>/Code/<project_name>.
        project_code_root_folder = os.path.join('Code', project.name)
        project.install_task = project.add_install_files(
            install_to = project.env.INCLUDE_INSTALL_PATH,
            install_from = generated_header_files,
            cwd = project.path.get_bld().find_node(project_code_root_folder),
            relative_trick = True,
            env = project.env,
            postpone = True)

