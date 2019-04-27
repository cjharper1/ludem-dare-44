from __future__ import absolute_import, division, print_function

from Waf.Utilities import LoadTools

## \package Waf.Installation
## This package contains tools for deploying the build to servers.

## Adds the options for current tool and all sub-tools. This method is executed before the current
## command context is initialized.
## \param[in] options_context - The options context is shared by all user defined options methods.
def options(options_context):
    return
    LoadTools(options_context, __file__)

## Initializes the command context for the current tool and all sub-tools. This method is executed
## before the user defined command methods.
## \param[in] command_context - The command context is shared by all user defined initialization
## methods.
def init(command_context):
    return
    LoadTools(command_context, __file__)

## Configures the environment for the current tool and all sub-tools.
## \param[in] configure_context - The configure context is shared by all user defined configure
## methods.
def configure(configure_context):
    return
    LoadTools(configure_context, __file__)
