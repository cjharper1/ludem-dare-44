from __future__ import absolute_import, division, print_function

import shutil
import os

from waflib import Logs
from waflib.Build import BuildContext

from Waf.Utilities import GetTargetProjects

## \package Waf.Utilities.Clean
## This package defines the 'clean' command.

## Deletes all build outputs for target projects. This command overrides the
## built-in Waf command. The built-in command deletes all build outputs
## regardless of targets. The new command is more convenient for a large code
## base.
##
## The command deletes outputs for projects that share the same build
## directory. This limitation was accepted for simplicity. Two projects can
## share the same build directory in two ways. First, they share the same Waf
## script. Second, the Waf script for one project is in a sub-directory
## relative to another project.
class CleanContext(BuildContext):
    # A command line description is not specified because it cannot replace the
    # the default.
    cmd = 'clean'

    # Executes the command. The method disables the actual build.
    def execute_build(self):
        # PROJECTS ARE RESTRICTED BASED ON THE COMMAND CONTEXT.
        # This provides consistent target semantics across all commands.
        projects = GetTargetProjects(self)

        # DELETE ALL OUTPUTS OF EACH PROJECT.
        # This technique will delete outputs for projects that share the same
        # build directory. This limitation is discussed in the class
        # documentation.
        build_dirs = set([
            project.path.get_bld() for project in projects])
        for build_dir in build_dirs:
            # BUILD DIRECTORIES ARE CREATED BY OTHER COMMANDS.
            # If no other command has been run, they will not exist.
            dir_exists = os.path.exists(build_dir.abspath())
            if not dir_exists:
                continue

            # DELETE FILES AND FOLDERS RECURSIVELY.
            try:
                shutil.rmtree(build_dir.abspath())
            except OSError:
                Logs.warn('Could not delete ' + build_dir.abspath())

