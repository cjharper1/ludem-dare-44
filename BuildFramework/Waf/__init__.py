from __future__ import absolute_import, division, print_function

from waflib import ConfigSet
from waflib import Options
from waflib.Build import BuildContext

from Waf.Utilities import LoadTools

## \package Waf
## This package contains the custom commands and tools created using the Waf build system framework.

## Adds the options for current tool and all sub-tools. This method is executed before the current
## command context is initialized.
## \param[in] options_context - The options context is shared by all user defined options methods.
def options(options_context):
    # ADD THE PYTHON TOOL OPTIONS.
    # The python tools allows task generators to verify whether a Python module is installed during
    # configuration. The options must be loaded for the tool to be used.
    options_context.load('python')
    
    # ADD THE MD5 TIMESTAMP TOOL.
    # This allows waf to re-calculate the MD5 hashes of files only when the timestamps of the files
    # have changed. For large builds, hashing can take several minutes and requires significant disk
    # I/O, so this tool can significantly improve the responsiveness of waf build commands.
    options_context.load('md5_tstamp')

    # THE VARIANT ISOLATES SETTINGS AND OUTPUTS.
    # This option is defaulted based on the last known value, and can be used
    # with any command (not just build).
    options_context.add_option(
        '--variant',
        help = 'The variant name.')

    # GET THE EXISTING CONFIGURATION OPTION GROUP, TO ADD THE NEW OPTIONS TO.
    # The options are used when building, but they are expected to be set at configure time.
    configuration_option_group = options_context.get_option_group('Configuration options')

    # THE CPU TARGET IS USED TO CONFIGURE COMPILATION.
    # The default is 64-bit.
    configuration_option_group.add_option(
        '--cpu',
        choices = ['x64', 'x86'],
        default = 'x64',
        help = 'The CPU target of the C++ and .NET compilers. [default: %default]')

    # DEBUGGING SYMBOLS MAY BE ENABLED.
    configuration_option_group.add_option(
        '--symbols',
        action='store_true',
        default = False,
        help = 'Generate debugging symbols.')

    # OPTIMIZATIONS MAY BE ENABLED.
    configuration_option_group.add_option(
        '--optimize',
        action='store_true',
        default = False,
        help = 'Perform optimizations.')

    # OBFUSCATION MAY BE ENABLED.
    configuration_option_group.add_option(
        '--obfuscate',
        action='store_true',
        default = False,
        help = 'Perform obfuscation on Web code and executables. ')

    # ADD THE OPTIONS FOR CUSTOM WAF TOOLS.
    LoadTools(options_context, __file__)

## Initializes the command context for the current tool and all sub-tools. This method is executed
## before the user defined command methods.
## \param[in] command_context - The command context is shared by all user defined initialization
## methods.
def init(command_context):
    # LOAD THE OPTIONS FROM THE CACHE.
    # Some options are defaulted based on the last known value.
    LoadOptionsFromStorage()

    # SET THE VARIANT FOR ALL COMMANDS.
    # All commands derive from the build command to access the task generators of the code base. The
    # variant is a static field that is inherited by all derived classes.
    BuildContext.variant = Options.options.variant

    # INITIALIZE THE COMMAND CONTEXT FOR CUSTOM WAF TOOLS.
    LoadTools(command_context, __file__)

## Configures the environment for the current tool and all sub-tools.
## \param[in] configure_context - The configure context is shared by all user defined configure
## methods.
def configure(configure_context):
    # SET THE VARIANT.
    configure_context.setenv(Options.options.variant)

    # CONFIGURE THE PYTHON TOOL ENVIRONMENT.
    # The Python tool adds methods like 'check_python_module' to the configure command context.
    configure_context.load('python')

    # STORE THE BUILD OPTIONS.
    # The options are stored so that they do not have to be respecified each
    # time the code is built.
    configure_context.env.CPU = Options.options.cpu
    configure_context.env.OBFUSCATE = Options.options.obfuscate
    configure_context.env.OPTIMIZE = Options.options.optimize
    configure_context.env.SYMBOLS = Options.options.symbols

# The value of certain options are persisted between commands. If an option is unspecified, then it
# is defaulted to the last known value. If no value is known, then a static default is used.
#
# In some cases, it is simpler to default an option to the last known value, instead of a static
# constant.
# - Build variant - A developer can define the build variant in the configuration command and then
#    exclude it from subsequent commands.
# - Product version - The Jenkins job pipeline separates the build and install commands. Both jobs
#    must configure the build variant. In build, the variant is created. In install, the product
#    version is set. The product version must not be reset in build for efficiency. However, the
#    product version is difficult to specify in build because it is based on the Jenkins build
#    number of install. A simple solution is to share the product version using the last known
#    value.
def LoadOptionsFromStorage():
    # LOAD THE OPTIONS FROM STORAGE.
    # The values are preserved between commands using the file system.
    options_storage_path = 'build/c4che/options.py'
    option_values = ConfigSet.ConfigSet()
    try:
        option_values.load(options_storage_path)
    except:
        pass

    # LOAD THE VARIANT OPTION.
    variant_option_specified = (
        hasattr(Options.options, 'variant') and
        (Options.options.variant is not None))
    if variant_option_specified:
        # The option is set by the user.
        variant = Options.options.variant
    else:
        # The option is set to the last known value or the static default.
        DEFAULT_VARIANT = 'default'
        variant = option_values.variant or DEFAULT_VARIANT

    # STORE THE OPTIONS IN THE CACHE.
    # The cache is created if it does not exist.
    option_values.variant = variant
    option_values.store(options_storage_path)

    # UPDATE THE OPTIONS IN MEMORY.
    Options.options.variant = variant
