from __future__ import absolute_import, division, print_function

from waflib import Errors
from waflib import Utils
from waflib.TaskGen import after_method
from waflib.TaskGen import before_method
from waflib.TaskGen import feature

## \package Waf.Dependency.AbstractDependency
## Add a dependency between projects. If a project A depends on a project B,
## then all outputs of A must be written before any task in project B is
## executed.
##
## The following example shows how to add an abstract dependency between two
## projects.
##
## \code
##     bld(
##         rule = 'echo "Project A"',
##         name = 'ProjectA')
##
##     bld(
##         rule = 'echo "Project B"',
##         name = 'ProjectB',
##         depends_on = ['ProjectA'])
## \endcode
##
## The build logs will show "Project A" before "Project B"

## Adds a dependency on all specified projects. All outputs of the specified
## projects are written before any task of the current project.
## \param[in,out] project - The dependencies are specified by the 'depends_on'
## attribute. A dependency is added to each of the project's tasks.
@feature('*')
@after_method('process_rule')
@after_method('apply_link')
@after_method('CompileDotNetProject')
def AddAbstractDependencies(project):
    # GET THE PROJECT DEPENDENCIES.
    dependency_projects = []
    dependency_names = Utils.to_list(getattr(project, 'depends_on', []))
    for dependency_name in dependency_names:
        # FIND THE PROJECT DEPENDENCY.
        try:
            dependency_project = project.bld.get_tgen_by_name(dependency_name)
        except Errors.WafError:
            error_msg = 'The project name is not valid: ' + dependency_name
            raise Errors.WafError(error_msg)

        # LOAD THE PROJECT DEPENDENCY.
        dependency_project.post()

        # STORE THE PROJECT DEPENDENCY.
        dependency_projects.append(dependency_project)

    # ADD THE DEPENDENCIES.
    for dependency_project in dependency_projects:
        for dependency_task in dependency_project.tasks:
            for task in project.tasks:
                task.dep_nodes.extend(dependency_task.outputs)

