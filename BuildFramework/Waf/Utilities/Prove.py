from __future__ import absolute_import, division, print_function

from collections import defaultdict
import itertools

from waflib.Build import BuildContext

from Waf.Dependency.Parents import GetImmediateParents
from Waf.Utilities import GetTargetProjects

## \package Waf.Utilities.Prove
## This package defines the 'prove' command.

## Proves that changes to the given targets are healthy by building all children. The command will
## also run child tests if tests are enabled.
class ProveContext(BuildContext):
    '''proves the health of the given targets by building all children.'''
    cmd = 'prove'

    # Extends the build targets to include all children.
    def pre_build(self):
        # PRESERVE THE BEHAVIOR OF THE BUILD COMMAND.
        super(ProveContext, self).pre_build()

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
                children_by_parent_name[parent_name].add(project)

        # TARGET PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        target_projects = GetTargetProjects(self)

        # BUILD ALL CHILDREN OF THE GIVEN TARGETS.
        visited_target_names = set()
        while target_projects:
            # VISIT EACH TARGET EXACTLY ONCE.
            target_project = target_projects.pop()
            already_visited = target_project.name in visited_target_names
            if already_visited:
                continue
            else:
                visited_target_names.add(target_project.name)

            # BUILD THE CURRENT PROJECT.
            # If the project has already been built, then the result will be cached.
            target_project.post()

            # VISIT ALL CHILDREN.
            child_projects = children_by_parent_name[target_project.name]
            target_projects.extend(child_projects)
