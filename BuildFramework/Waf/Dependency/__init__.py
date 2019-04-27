from __future__ import absolute_import, division, print_function

import types

from Waf.Utilities import LoadTools

## \package Waf.Dependency
## This package contains tools for expressing dependencies between task generators and commands that
## exploit the dependency tree.
##
## The Waf build context, task generator, and task classes provide an API for creating dependencies.
## In the Waf script, dependencies are expressed between task generators using their name.
##
## ~~~ {.py}
## ## Demonstrates the the use of a Waf tool that expresses high level dependencies between task
## ## generators.
## def build(bld):
##     # The parent task generator can be defined anywhere in the code base.
##     bld(
##         features = 'my_feature',
##         name = 'ParentTask')
##
##     # The child task generator can refer to the parent by name.
##     bld(
##         features = 'my_feature',
##         name = 'ChildTask',
##         my_parent = 'ParentTask')
## ~~~
##
## A task generator method can use the Waf build context to lookup the parent when creating child
## tasks.
##
## ~~~ {.py}
## from waflib.Task import Task
## from waflib.TaskGen import feature
##
## ## Demonstrates how a Waf tool can translate high level dependencies between task generators into
## ## dependencies between their tasks.
## @feature('my_feature')
## def MyFeatureMethod(project):
##     # GET THE PARENT PROJECT NAME.
##     # A parent project is optional.
##     try:
##         parent_project_name = project.my_parent
##     except AttributeError:
##         # A parent was not specified.
##         return
##
##     # GET THE PARENT PROJECT.
##     # A task generator can use the build context class to lookup the parent task generator by
##     # name. All task generators in the code base are indexed before the task generator method is
##     # called.
##     try:
##         build_context = project.bld
##         parent_project = build_context.get_tgen_by_name(parent_project_name)
##     except WafError:
##         # The parent project does not exist.
##         return
##
##     # GENERATE THE PARENT TASKS.
##     # The post method returns when all methods of the task generator have been executed. A task
##     # generator is only posted once. Since the parent project has the same feature, this method
##     # will be called for the parent recursively.
##     parent_project.post()
##
##     # CREATE A TASK.
##     # The task base class does nothing. See the main page on task generator methods on how to new
##     # tasks. The build context class requires that all tasks are stored in the 'tasks' attribute
##     # of the task generator.
##     project.my_task = Task()
##     project.tasks.append(my_task)
##
##     # ADD A DEPENDENCY BY CONSUMING THE OUTPUTS OF THE PARENT TASK.
##     # The outputs of the parent can be consumed as inputs or dependent nodes. The attributes are
##     # semantically equivalent. If any of the parent outputs change, the task will be re-run.
##     project.my_task.inputs = parent_project.my_task.outputs
##     project.my_task.dep_nodes = parent_project.my_task.outputs
##
##     # ADD A DEPENDENCY BY RUNNING AFTER THE PARENT TASK.
##     # The task must be run after the parent has executed, but if the parent outputs change, the
##     # task is not rerun. This type of dependency is rare, but can be useful. For example, if a
##     # C++ application uses a C# application at runtime, then the C# application should be built
##     # before the C++ application. However, if the C# application changes, the C++ application
##     # does not need to be rebuilt.
##     project.my_task.set_run_after(parent_project.my_task)
## ~~~

## Adds the options for the current tool and all sub-tools. This method is executed before the
## current command context is initialized.
## \param[in] options_context - The options context is shared by all user defined options methods.
def options(options_context):
    LoadTools(options_context, __file__)

## Initializes the command context for the current tool and all sub-tools. This method is executed
## before the user defined command methods.
## \param[in] command_context - The command context is shared by all user defined initialization
## methods.
def init(command_context):
    LoadTools(command_context, __file__)

## Configures the environment for the current tool and all sub-tools.
## \param[in] configure_context - The configure context is shared by all user defined configure
## methods.
def configure(configure_context):
    LoadTools(configure_context, __file__)

## A task is an edge in the build graph. It connects a set of input nodes to a
## set of output nodes. Caching and dependency analysis require that every
## output node in the build graph is produced by a single task. Sub-tasks are
## used to perform additional operations on outputs.
##
## A task can be thought of as a series of methods that produce an output. Each
## of these methods is a sub-task. This method allows sub-tasks to be added
## after the task has been created. This is useful when sub-tasks are optional
## or defined by independent build system features.
## \param parent_task - The task object to extend.
## \param sub_task - The method to add as a sub-task. The method takes the
## parent task as its only argument. It will be executed only after all
## previous sub-tasks have completed successfully.
def AddSubTask(parent_task, sub_task):
    # LOAD THE PREVIOUS SUB-TASKS.
    # The "run" attribute stores a chain of methods that produce the outputs of
    # the task. The methods are chained together through wrapping.
    previous_sub_tasks = parent_task.run

    # DEFINE A METHOD TO RUN THE ADDITIONAL SUB-TASK.
    # The interface is designed to match the run method of the Task class. See
    # the Task class for possible return values.
    def RunSubTask(self):
        # RUN THE PREVIOUS SUB-TASKS.
        # The previous sub-tasks take no parameters because the method has
        # already been bound to the parent task object.
        TASK_SUCCESSFUL = 0
        previous_sub_tasks_result = previous_sub_tasks()
        previous_sub_tasks_successful = (
            TASK_SUCCESSFUL == previous_sub_tasks_result)
        if not previous_sub_tasks_successful:
            # Return the error that occurred.
            return previous_sub_tasks_result

        # RUN THE NEW SUB-TASK.
        # The method is given an instance to the parent task.
        sub_task_result = sub_task(self)
        sub_task_sucessful = (TASK_SUCCESSFUL == sub_task_result)
        if not sub_task_sucessful:
            # Return the error that occurred.
            return sub_task_result

        # ALL SUB-TASKS WERE SUCCESSFUL.
        return TASK_SUCCESSFUL

    # ADD THE SUB-TASK TO THE CHAIN.
    # The method type class binds the wrapper method to the parent task object.
    parent_task_run_method = types.MethodType(
        RunSubTask,
        parent_task,
        type(parent_task))
    parent_task.run = parent_task_run_method

