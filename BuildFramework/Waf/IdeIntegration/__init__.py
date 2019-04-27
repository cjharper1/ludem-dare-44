from __future__ import absolute_import, division, print_function

from Waf.Utilities import LoadTools

## \package Waf.IdeIntegration
## This package contains command and tools for generating IDE project files.
##
## \todo The class abstractions used to read meta-data from supported language projects are useful
## in other contexts. The classes could be grouped with compilation or assigned a new subsystem.

## Adds the options for current tool and all sub-tools. This method is executed before the current
## command context is initialized.
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
