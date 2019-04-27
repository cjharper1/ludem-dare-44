from __future__ import absolute_import, division, print_function

from collections import defaultdict
import itertools

from waflib.Build import BuildContext
from waflib import Logs

from Waf.Dependency.Parents import GetImmediateParents
from Waf.Utilities import GetTargetProjects

## \package Waf.Dependency.Children
## This package defines the 'children' command.

## Lists the top-level children of the given targets.
class Children(BuildContext):
    '''prints the top-level child dependencies of the target projects.'''
    cmd = 'children'

    # Creates a parent-child lookup for all projects. This must be done in pre_build().
    def pre_build(self):
        # GATHER THE CHILDREN OF ALL PROJECTS.
        # A project expresses parent dependencies using the 'use', 'depends_on', 'runs_after'
        # or dynamic attribute. The children are gathered up front so that the algorithm can
        # efficiently traverse the project tree from parent to children.
        children_by_parent_name = defaultdict(set)
        projects = list(itertools.chain.from_iterable(self.groups))
        for project in projects:
            # Get the immediate parents of the project.
            parent_names = GetImmediateParents(project)

            # Add this project as a child of its parent project.
            for parent_name in parent_names:
                children_by_parent_name[parent_name].add(project.name)

        # TARGET PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        target_projects = GetTargetProjects(self)

        # PRINT CHILDREN OF SPECIFIED TARGETS.
        for project in target_projects:
            Logs.info('{}: {}'.format(project.name, sorted(children_by_parent_name[project.name])))

    # Overrides the default compile() to prevent the target projects from building.
    def compile(self):
        pass
