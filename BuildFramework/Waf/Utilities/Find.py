from __future__ import absolute_import, division, print_function

from waflib import Context
from waflib import Logs
from waflib import Options
from waflib.Build import BuildContext

from Waf.Utilities import GetTargetProjects
from Waf.Utilities import OpenFileInDefaultProgram

## \package Waf.Utilities.Find
## This package defines the 'find' command.

## Prints the wscript path at which each of the target projects is defined, to assist the user in
## locating the wscript that defines each target. The wscripts are also opened automatically 
## if requested (via --open).
class FindContext(BuildContext):
    '''finds the waf script in which the target is defined'''
    cmd = 'find'

    # Executes the command. The method disables the actual build.
    def execute_build(self):
        # PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        projects = GetTargetProjects(self)

        # PRINT THE PROJECTS' WSCRIPT PATHS (AND OPEN THEM IF REQUESTED).
        for project in projects:
            wscript_path = project.path.make_node(Context.WSCRIPT_FILE).abspath()
            Logs.info("{}: {}".format(project.name, wscript_path))
            
            # Open the wscript if requested, in the default program.
            if Options.options.open:
                OpenFileInDefaultProgram(wscript_path)
