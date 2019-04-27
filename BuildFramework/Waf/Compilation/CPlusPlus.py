from __future__ import absolute_import, division, print_function

import sys

from waflib import Context
from waflib import Logs
from waflib import Utils
from waflib.Errors import WafError
from waflib.Task import Task
from waflib.TaskGen import after_method
from waflib.TaskGen import before_method
from waflib.TaskGen import extension
from waflib.TaskGen import feature
from waflib.Tools import cxx

from Waf.Dependency import AddSubTask

## \package Waf.Compilation.CPlusPlus
## This package adds support for the C++ language. It extends the C++ tools provided by Waf for
## simplicity. The C++ tools are extended by adding to pre-defined environment variables or adding
## additional sub-tasks to compilation.
##
## The Waf C++ tool implements a custom preprocessor to calculate the header file dependencies of
## each implementation file. The custom preprocessor is required to cache C++ compilation, but
## consumes a large part of pre-build resources.

# The GCC symbols are stripped from the executable and copied to an external
# file. A two-part executable (similar to using a Visual Studio PDB) is
# required to deliver products to the customer. Products must be delivered
# without debugging symbols to protect our intellectual property. However, our
# developers must be able debug errors in the context they occur. With a
# two-part executable, the symbols can be excluded from delivery and copied to
# field servers to debug errors.
#
# The GNU toolchain provides a tool called 'objcopy' to separate symbols from
# a GCC compiled binary. GCC cannot separate the symbols during compilation.
#
# \param[in,out] project - The C++ executable is given as an output of the
# linker task. The linker task is created by the 'apply_link' method. If the
# project is an executable, then a new task is added to separate the symbols.
# It is risky to add a task to the built-in C++ feature because it will not be
# considered in the built-in dependency analysis. It is safe in this case
# because C++ projects only depend on libraries and not executables. Also, new
# project level dependencies make sure to consider all tasks in a project.
@feature('c','cxx')
@after_method('apply_link')
def SeparateSymbolsFromGccExecutable(project):
    # VERIFY THAT GCC IS BEING USED.
    using_gcc = ('gcc' == project.env.CXX_NAME)
    if not using_gcc:
        return

    # CHECK THAT AN EXECUTABLE IS BEING BUILT.
    try:
        is_exe = isinstance(project.link_task, cxx.cxxprogram)
    except AttributeError:
        is_exe = False
    if not is_exe:
        return

    # CHECK IF SYMBOLS ARE ENABLED.
    has_symbols = project.env.SYMBOLS
    if not has_symbols:
        return

    # ADD A SUB-TASK TO SEPARATE THE SYMBOLS.
    AddSubTask(project.link_task, SeparateSymbolsFromGccExecutableSubTask)

## The GCC symbols are stripped from the executable and copied to an external
## file. This method executes the associated commands at build-time. See the
## feature method for more details on symbols separation.
## \param parent_task - The parent task object to extend.
## \returns Zero if successful, greater than zero otherwise.
def SeparateSymbolsFromGccExecutableSubTask(parent_task):
    # COPY THE SYMBOLS FROM THE EXECUTABLE TO AN EXTERNAL FILE.
    exe_node = parent_task.outputs[0]
    sym_node = exe_node.change_ext('.sym')
    copy_symbols_cmd = (
        'objcopy --only-keep-debug "{exe_path}" "{sym_path}"').format(
        exe_path = exe_node.abspath(),
        sym_path = sym_node.abspath())
    copy_symbols_result = parent_task.exec_command(copy_symbols_cmd)
    CMD_SUCCESSFUL = 0
    symbols_copied = (CMD_SUCCESSFUL == copy_symbols_result)
    if not symbols_copied:
        return copy_symbols_result

    # REMOVE THE SYMBOLS FROM THE EXECUTABLE.
    remove_symbols_cmd = 'objcopy --strip-all "{exe_path}"'.format(
        exe_path = exe_node.abspath())
    remove_symbols_result = parent_task.exec_command(remove_symbols_cmd)
    symbols_removed = (CMD_SUCCESSFUL == remove_symbols_result)
    if not symbols_removed:
        return remove_symbols_result

    # INSTRUCT GDB TO LOAD THE EXTERNAL SYMBOLS WHEN PRESENT.
    # The command is executed in the same directory as the executable to
    # to instruct GDB to look for the symbols in the current directory.
    link_to_external_symbols_cmd = (
        'objcopy --add-gnu-debuglink={sym_name} "{exe_path}"').format(
        exe_path = exe_node.abspath(),
        sym_name = sym_node.name)
    exe_dir = exe_node.parent.abspath()
    link_result = parent_task.exec_command(link_to_external_symbols_cmd, cwd = exe_dir)
    symbols_linked = (CMD_SUCCESSFUL == link_result)
    if not symbols_linked:
        return link_result

    # THE SYMBOLS WERE STRIPPED SUCCESSFULLY.
    return 0

# C++ executables are installed along side their external symbols.
# \param[in,out] project - The C++ executable is given as an output of the
# linker task. The linker task is created by the 'apply_link' method. The
# external symbols files are added as inputs to the installation task.
@feature('c','cxx')
@after_method('apply_link')
@after_method('apply_flags_msvc')
def InstallExecutablesWithSymbols(project):
    # VERIFY THAT AN INSTALLATION WITH SYMBOLS IS BEING PERFORMED.
    has_symbols = project.env.SYMBOLS
    if not has_symbols:
        return

    # CHECK THAT AN EXECUTABLE IS BEING BUILT.
    try:
        # A C++ shared object is a subtype of a C++ program, probably because they're linked and built in much
        # the same way.  Shared objects are not actuall programs and do not have symbols files.
        is_exe = isinstance(project.link_task, cxx.cxxprogram) and not isinstance(project.link_task, cxx.cxxshlib)
    except AttributeError:
        is_exe = False
    if not is_exe:
        # Symbols are only available for executables.
        return

    # INSTALL THE SYMBOLS BASED ON THE SUPPORTED COMPILER.
    using_gcc = ('gcc' == project.env.CXX_NAME)
    using_visual_studio = ('msvc' == project.env.CXX_NAME)
    symbols_files = []
    if using_gcc:
        # INSTALL THE SYMBOLS FILE.
        exe_node = project.link_task.outputs[0]
        sym_node = exe_node.change_ext('.sym')
        project.link_task.outputs.append(sym_node)
        symbols_files.append(sym_node)

    elif using_visual_studio:
        # INSTALL THE MAP FILE.
        # The PDB file is already installed by the Visual C++ feature.
        exe_node = project.link_task.outputs[0]
        map_node = exe_node.change_ext('.map')
        project.link_task.outputs.append(map_node)
        symbols_files.append(map_node)

    # UPDATE THE INSTALLATION TASK.
    is_installation = project.bld.cmd in ('install', 'uninstall')
    if is_installation:
        # The symbols files must be set up to be installed.
        project.install_task.inputs.extend(symbols_files)
        install_node = project.bld.root.make_node(project.install_task.get_install_path())
        project.install_task.outputs.extend([install_node.make_node(symbols_file.name) for symbols_file in symbols_files])

## Applies custom manifests to the given project, mainly for GUI applications.
## Only applies to Visual Studio projects. The method must be run after the link
## tasks are created or else the output executable will not be known.
## Any project with custom manifests must have them specified as the project's
## 'manifest_files' attribute.
## \param[in,out] project - The project for which to apply custom manifests.
@feature('c','cxx')
@after_method('apply_link')
def ApplyCustomManifests(project):
    # This is only applicable to Visual Studio.
    using_visual_studio = ('msvc' == project.env.CXX_NAME)
    if not using_visual_studio:
        return

    # GET THE MANIFEST FILES.
    manifest_files = list(project.to_nodes(getattr(project, 'manifest_files', [])))
    manifest_files_specified = (len(manifest_files) != 0)
    if not manifest_files_specified:
        return

    # ADD A SUB-TASK TO APPLY THE CUSTOM MANIFESTS.
    project.manifest_files = manifest_files
    AddSubTask(project.link_task, ApplyCustomManifestsSubTask)

## Custom manifests to an exe or DLL.
## See the feature method for more information on how the custom manifests are applied.
## \param parent_task - The parent task object to extend.
## \returns Zero if successful, non-zero otherwise.
def ApplyCustomManifestsSubTask(parent_task):
    # CATEGORIZE THE OUTPUT RESOURCE.
    output_node = parent_task.outputs[0]
    is_exe = (output_node.suffix() == '.exe')
    EXE_MODE = 1
    DLL_MODE = 2
    resource_id = EXE_MODE if is_exe else DLL_MODE

    # FORM THE COMMAND TO CALL THE MANIFEST TOOL.
    # See http://msdn.microsoft.com/en-us/library/aa375649%28v=vs.100%29.aspx for more info.
    # Multiple manifests can be specified in a single call by forming a space-separated list.
    get_quoted_path = lambda node: '"{}"'.format(node.abspath())
    manifest_tool_path = Utils.subst_vars('"${MT}"', parent_task.env)
    manifest_file_nodes = parent_task.generator.manifest_files
    quoted_manifest_paths = ' '.join(map(get_quoted_path, manifest_file_nodes))
    manifest_tool_command = ' '.join([
        '{manifest_tool}',
        '-manifest {manifest_paths}',
        '-outputresource:{exe_path};{resource_id}']).format(
        manifest_tool = manifest_tool_path,
        manifest_paths = quoted_manifest_paths,
        exe_path = get_quoted_path(output_node),
        resource_id = resource_id)

    # CALL THE MANIFEST TOOL.
    manifest_tool_result = parent_task.exec_command(manifest_tool_command)
    return manifest_tool_result


# The C++ header files cannot be compiled. They are ignored here to that they
# are not further processed by Waf.
@extension('.h')
def IgnoreHeaderFiles(project, node):
    pass

# Patch older versions of waf where the preprocessor's cache is sized too small by default.
if Utils.num2ver('1.9.7') > Context.HEXVERSION:
    Logs.warn('Please upgrade to waf 1.9.7 for improved performance!')
    
    # Monkey-patch the built-in cached_find_resource method for Waf's custom preprocessor. In waf version 
    # 1.9, the node cache was changed from a dict to an LRU cache in order to reduce memory consumption 
    # (see https://github.com/waf-project/waf/commit/4e09a1bc5ac03bd74204aeb0ccc4f08f56d870e3), but it's 
    # sized so small that it results in a high cache miss rate for large builds. This patch allows us to 
    # get back the old behavior (unlimited sized cache) without changing the waf source code. If the 
    # preproc_cache_node member variable name is changed, this patch will have to be updated accordingly.
    # The patch wraps the existing method with logic to ensure that the cache is always set to use a 
    # plain dict, so that an LRU cache will never be used.
    from waflib.Tools import c_preproc
    _old_cached_find_resource = c_preproc.c_parser.cached_find_resource
    def _cached_find_resource(self, node, filename):
        # Check if a cache is already available.
        cache_available = hasattr(node.ctx, 'preproc_cache_node')
        if not cache_available:        
            # Set up an unlimited-size cache (a plain dict).
            node.ctx.preproc_cache_node = {}
            
        # Execute the original method.
        return _old_cached_find_resource(self, node, filename)
    c_preproc.c_parser.cached_find_resource = _cached_find_resource
