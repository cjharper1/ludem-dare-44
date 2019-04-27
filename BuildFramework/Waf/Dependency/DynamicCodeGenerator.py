from __future__ import absolute_import, division, print_function

import sys

from waflib import Errors
from waflib import Utils
from waflib.TaskGen import after_method
from waflib.TaskGen import before_method
from waflib.TaskGen import feature

## \package Waf.Dependency.DynamicCodeGenerator
## While some code generation tools are from a third party, others are built
## from source. The project must ensure that the tool is built before being
## used.
##
## The following example shows how to generate code using a tool that is built
## from source.
##
## \code
##     bld(
##         rule = '${GENERATOR_PATH} Parameter ${SRC} ${TGT}',
##         features = 'DynamicCodeGenerator',
##         code_generator = 'CodeGeneratorName',
##         source = 'Path/To/GeneratorInput',
##         target = 'Path/To/GeneratedCode',
##         name = 'GeneratedCode')
## \endcode

## Provides access to the code generator executable path via the project's
## local environment. The method must be executed before 'process_rule' or else
## the environment variable will be ignored.
## \param[in,out] project - The code generator's project name is specified in
## the 'code_generator' attribute. The absolute path is stored in the
## 'GENERATOR_PATH' environment variable.
@feature('DynamicCodeGenerator')
@before_method('process_rule')
def SetCodeGeneratorPath(project):
    # GET THE CODE GENERATOR'S PROJECT NAME.
    generator_name = getattr(project, 'code_generator', None)
    if not generator_name:
        error_msg = 'Please specify a code generator name: ' + project.name
        raise Errors.WafError(error_msg)

    # RESOLVE THE CODE GENERATOR PROJECT.
    # The name must reference an existing project.
    try:
        generator_project = project.bld.get_tgen_by_name(generator_name)
    except Errors.WafError:
        error_msg = ('{project_name} at {project_dir} - The code generator '
            'name is invalid: {generator_name}').format(
            project_name = project.name,
            project_dir = project.path.path_from(project.bld.srcnode),
            generator_name = generator_name)
        raise Errors.WafError(error_msg)

    # LOAD THE CODE GENERATOR PROJECT.
    generator_project.post()

    # GATHER ALL EXECUTABLE OUTPUTS.
    executable_outputs = []
    for task in generator_project.tasks:
        is_executable = lambda output: (output.suffix() in [output.name, '.exe'])
        executable_outputs.extend([
            output for output in task.outputs
            if is_executable(output)])

    # CHECK IF A GENERATOR IS AVAILABLE.
    is_generator_available = (len(executable_outputs) >= 1)
    if not is_generator_available:
        error_msg = (
            'The code generator project does not produce an executable: ' +
            generator_name)
        raise Errors.WafError(error_msg)

    # STORE THE CODE GENERATOR DEPENDENCIES.
    # The project is used to wait for the generator to be built. The executable
    # is used to re-generate code when the generator changes.
    project.code_generator_project = generator_project
    project.code_generator_exe = executable_outputs.pop()

    # PROVIDE ACCESS TO THE CODE GENERATOR EXECUTABLE PATH.
    project.env.GENERATOR_PATH = project.code_generator_exe.abspath()

    # ENSURE THE CODE GENERATOR IS EXECUTABLE IN LINUX.
    # In linux, outputs of the Mono .NET compiler are not given executable
    # permissions.
    is_linux = ('linux' in sys.platform)
    is_dot_net = ('dot_net' in generator_project.features)
    mono_execution_required = is_linux and is_dot_net
    if mono_execution_required:
        project.env.GENERATOR_PATH = 'mono ' + project.env.GENERATOR_PATH

## The code generator executable must be built before it is used. The method
## must be executed after 'process_rule' or else the rule task will not exist.
## \param[in,out] project - The code generator executable is specified in the
## 'code_generator_exe' attribute. A dependency is added to the project's
## tasks.
@feature('DynamicCodeGenerator')
@after_method('process_rule')
def WaitForGeneratorBeforeUse(project):
    # GET THE CODE GENERATOR PROJECT.
    # If not found, the executable is not specified. An error has already been
    # reported.
    code_generator_project = getattr(project, 'code_generator_project', None)
    if not code_generator_project:
        return

    # MAKE SURE THE TOOL IS BUILT BEFORE WE USE IT.
    # A dependency will also regenerate the code if the executable is changed.
    for task in project.tasks:
        task.dep_nodes.append(project.code_generator_exe)
        for code_generator_task in code_generator_project.tasks:
            task.set_run_after(code_generator_task)

