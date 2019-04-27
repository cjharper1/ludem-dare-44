from __future__ import absolute_import, division, print_function

from waflib.Node import Node
from Waf.IdeIntegration.Project import Project

## \package Waf.IdeIntegration.CppProject
## This package defines an interface for task generators that represent a C++ project.

## Provides an interface for binding a Waf project to a C++ project template.
class CppProject(Project):
    # Provides binding for the given Waf project.
    def __init__(self, waf_project):
        self.waf_project = waf_project

    # The binary output of the compilation.
    def GetOutputFile(self):
        return self.waf_project.link_task.outputs[0]

    # The working directory of the application when run from the IDE.
    def GetDebugDir(self):
        # CHECK IF A CUSTOM DEBUG DIRECTORY IS DEFINED.
        # The expected working directory varies between applications. A custom directory is
        # supported only for backwards compatibility. New projects should use the default.
        has_custom_debug_dir = hasattr(self.waf_project, 'run_dir')
        if has_custom_debug_dir:
            debug_dir = self.waf_project.run_dir
        else:
            default_debug_dir = self.GetSourceDir()
            debug_dir = default_debug_dir

        # RETURN THE DEBUG DIRECTORY.
        return debug_dir

    # The pre-processor definitions used during compilation.
    def GetPreProcessorDefinitions(self):
        return self.waf_project.env.DEFINES

    # The include directories referenced during compilation.
    def GetIncludeDirs(self):
        # GET THE INCLUDES SEEN BY THE WAF C PREPROCESSOR.
        # Most includes are inherited from dependencies using the standard
        # "include" attribute.
        include_dirs = self.waf_project.includes_nodes

        # GET THE INCLUDES ADDED DIRECTLY TO THE COMMAND LINE.
        # The Boost includes are hidden from the Waf C Preprocessor because
        # they never change. See the Boost Waf script for more details.
        root_dir = self.waf_project.bld.srcnode
        add_include_path_format = self.waf_project.env['CPPPATH_ST']
        add_include_path_prefix = add_include_path_format.replace('%s', '')
        hidden_include_paths = [
            flag.replace(add_include_path_prefix, '')
            for flag in self.waf_project.env['CXXFLAGS']
            if flag.startswith(add_include_path_prefix)]

        # CONVERT THE HIDDEN INCLUDE PATHS TO NODES.
        root_dir = Node('', None)
        hidden_include_dirs = [
            root_dir.make_node(include_path)
            for include_path in hidden_include_paths]

        # RETURN ALL INCLUDE DIRECTORIES.
        include_dirs.extend(hidden_include_dirs)
        return include_dirs

    # The header files of the project.
    def GetHeaderFiles(self):
        # INCLUDE HEADER FILES.
        include_files = self.GetSourceDir().ant_glob('**/*.h')
        return include_files

    # The source files of the project.
    def GetSourceFiles(self):
        # EXCLUDE GENERATED FILES.
        # The symbols are imported from header files even if they are not part of the project.
        is_user_written = lambda file: not file.is_child_of(self.waf_project.bld.bldnode)
        source_files = self.waf_project.to_nodes(self.waf_project.source)
        user_written_files = [file for file in source_files if is_user_written(file)]
        return user_written_files

    # The source directory is the parent directory shared by all source files.
    def GetSourceDir(self):
        source_dir = super(CppProject, self).GetSourceDir(self.waf_project.source)
        return source_dir
