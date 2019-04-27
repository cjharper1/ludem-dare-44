from __future__ import absolute_import, division, print_function

from waflib import Errors
from waflib import Utils
from waflib.TaskGen import before_method
from waflib.TaskGen import feature

## \package Waf.Dependency.DynamicAttribute
## Projects may populate attributes with the outputs of other projects. To
## populate an attribute 'my_attr' with the outputs of a project 'MyProject',
## create an attribute with the following format:
##
## dynamic_my_attr = ['MyProject']
##
## The following example shows how a project may be built using dynamic source
## files from a code generation tool. It is for a C++ static library, so some
## differences will exist for other types of projects.
##
## \code
##     bld.stlib(
##         includes = 'IncludePath',
##         export_includes = 'IncludePath',
##         source = bld.path.ant_glob('Path/To/**/*.cpp'),
##         dynamic_source = 'GeneratedCode',
##         target = 'LibraryName')
## \endcode

## Populates all target attributes with outputs of specified projects.
## \param[in,out] project - Target attributes are specified with the 'dynamic_'
## prefix. The target attribute (prefix removed) is extended with the outputs
## of all specified projects.
@feature('*')
@before_method('process_rule')
def ResolveDynamicAttributes(project):
    # GATHER THE DYNAMIC ATTRIBUTES.
    is_dynamic_attribute = lambda attribute_name: (
        'dynamic_' in attribute_name)
    dynamic_attribute_names = [
        attribute_name for attribute_name in dir(project)
        if is_dynamic_attribute(attribute_name)]

    # INITIALIZE THE PROJECT DEPENDENCIES.
    project.runs_after = Utils.to_list(getattr(project, 'runs_after', []))

    # RESOLVE EACH DYNAMIC ATTRIBUTE.
    for dynamic_attribute_name in dynamic_attribute_names:
        # ENSURE THE PROJECT IS BUILT BEFORE USE.
        project_names = Utils.to_list(getattr(project, dynamic_attribute_name))
        project.runs_after.extend(project_names)

        # RESOLVE ALL REFERENCED PROJECTS.
        for project_name in project_names:
            # RESOLVE THE REFERENCED PROJECT.
            try:
                referenced_project = project.bld.get_tgen_by_name(project_name)
            except Errors.WafError:
                error_msg = 'The referenced project name is not valid: ' + project_name
                raise Errors.WafError(error_msg)

            # LOAD THE PROJECT.
            referenced_project.post()

            # GATHER THE REFERENCED OUTPUTS.
            referenced_outputs = []
            for task in referenced_project.tasks:
                referenced_outputs.extend(task.outputs)

            # GET THE EXISTING TARGET ATTRIBUTE.
            target_attribute_name = dynamic_attribute_name.split('dynamic_')[1]
            target_attribute = Utils.to_list(
                getattr(project, target_attribute_name, []))
            is_list = isinstance(target_attribute, list)
            if not is_list:
                target_attribute = [target_attribute]

            # EXTEND THE ATTRIBUTE WITH ALL REFERENCED OUTPUTS.
            target_attribute.extend(referenced_outputs)
            setattr(project, target_attribute_name, target_attribute)
