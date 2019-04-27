#! /usr/bin/env python
import os
import sys

from waflib import ConfigSet
from waflib import Options
from waflib.Build import BuildContext
from waflib.TaskGen import extension
from waflib.Errors import WafError


import re
import sys

from waflib import Logs

## This package customizes the log formatting used by Waf, to better emphasize errors, warnings, 
## and notes emitted by built tools.
           
## This is a custom log formatter that will colorize warnings, errors, and notes emitted by build
## tools, to make them more obvious to the user.
class CustomLogFormatter(Logs.formatter):
    ## Initializes the formatter by setting up the regexes used to classify log text.
    def __init__(self):        
        Logs.formatter.__init__(self)
        self.ErrorRegex = re.compile('(: error)|(: fatal error)|(: general error)')
        self.WarningRegex = re.compile(': warning')
        self.NoteRegex = re.compile('(: note)|(^NOTE:)')
        
    ## This performs the colorization of a log record's message.
    ## \param   log_record - The log record whose message is to be colorized.
    ## \return  The colorized log text.
    def format(self, log_record):
        # GET THE CURRENT STACK FRAME.
        frame = sys._getframe()
        
        # USE THE CALL STACK TO DETERMINE WHETHER TO COLORIZE THE LOG RECORD.
        while frame:
            # CHECK IF A COMMAND IS BEING EXECUTED.
            # Only try to colorize the logged text from commands being executed, to avoid messing 
            # up other logged text.
            function_name = frame.f_code.co_name
            is_executing_command = (function_name == 'exec_command')
            if not is_executing_command:
                # Move to the next frame in the call stack.
                frame = frame.f_back
                continue
                
            # COLORIZE EACH OF THE LINES ACCORDING TO WHAT THEY CONTAIN.
            # Errors are most important, so prioritize them over warnings, warnings over notes, and 
            # notes over normal information.
            lines = []
            for line in log_record.msg.splitlines():
                if self.__IsError(line):
                    lines.append(Logs.colors.RED + line)
                elif self.__IsWarning(line):
                    lines.append(Logs.colors.YELLOW + line)
                elif self.__IsNote(line):
                    lines.append(Logs.colors.CYAN + line)
                else:
                    lines.append(line)
                    
            # REPLACE THE LOG RECORD'S MESSAGE WITH THE COLORIZED VERSION.
            log_record.msg = '\n'.join(lines)
            break

        # PERFORM ADDITIONAL FORMATTING WITH THE BUILT-IN FORMATTER.
        return Logs.formatter.format(self, log_record)

    ## Determines if the text indicates an error.
    ## \param   text - The text to analyze.
    ## \return  True if the text indicates an error; False otherwise.
    def __IsError(self, text):
        return self.ErrorRegex.search(text)

    ## Determines if the text indicates a warning.
    ## \param   text - The text to analyze.
    ## \return  True if the text indicates a warning; False otherwise.
    def __IsWarning(self, text):
        return self.WarningRegex.search(text)

    ## Determines if the text indicates a note.
    ## \param   text - The text to analyze.
    ## \return  True if the text indicates a note; False otherwise.
    def __IsNote(self, text):
        return self.NoteRegex.search(text)

## Configures options available for waf commands.
## This runs before every command.
## \param[in]   opt - The current options context.
def options(opt):
    # LOAD CUSTOM PLUGINS AND COMMANDS.
    opt.load('Waf', tooldir = 'BuildFramework')
    
    # ADD AN OPTION TO ISOLATE BUILD OUTPUTS BASED ON SETTINGS.
    # This option is defaulted based on the last known value, and can be used
    # with any command (not just build).
    opt.add_option(
        '--variant',
        help = 'The variant name.')
        
    # GET THE EXISTING CONFIGURATION OPTION GROUP TO ADD NEW OPTIONS TO.
    configuration_option_group = opt.get_option_group('Configuration options')
    
    # THE CPU OPTION DETERMINES THE TARGET CPU FOR COMPILATION.
    # This is really only useful for Windows builds. It defaults to x64.
    configuration_option_group.add_option(
        '--cpu',
        choices = ['x64', 'x86'],
        default = 'x64')
        
    # ADD AN OPTION TO ENABLE DEBUG SYMBOLS.
    configuration_option_group.add_option(
        '--symbols',
        action ='store_true',
        default = False)
        
    # ADD AN OPTION TO ENABLE OPTIMIZATION.
    configuration_option_group.add_option(
        '--optimize',
        action ='store_true',
        default = False)

    # LOAD THE OPTIONS PROVIDED FOR C++ TASKS.
    # These are provided via the Waf library.
    opt.load('compiler_cxx')
    
    # Remove MSVC-specific options programmatically defined by 
    # Waf to avoid confusion with the --version and --targets commands.
    # There is no way to determine if these were actually loaded, and MSVC
    # may not be present on the system. Therefore, a try/catch is needed.
    try:
        opt.parser.remove_option('--msvc_targets')
        opt.parser.remove_option('--msvc_version')
    except ValueError:
        # MSVC is not on this system. This is not necessarily an error.
        pass
        
## Initializes the current command context. This runs before every waf command.
## \param[in]   command_context - The command context being initialized.
def init(command_context):
    # LOAD CUSTOM PLUGINS AND COMMANDS.
    command_context.load('Waf', tooldir = 'BuildFramework')
    
    # SET WAF TO LOG WARNINGS AND ERRORS WITH CUSTOM COLORS.
    Logs.log.handlers[0].setFormatter(CustomLogFormatter())
    
    # ATTEMPT TO LOAD ANY OPTIONS SPECIFIED ON THE PREVIOUS COMMAND.
    options_storage_path = 'build/c4che/options.py'
    option_values = ConfigSet.ConfigSet()
    try:
        option_values.load(options_storage_path)
    except:
        pass
        
    # DETERMINE WHICH VARIANT TO USE FOR THE CURRENT COMMAND.
    # The user can explicitly specify a variant to use via command line option or they can default to the most recently used variant
    # by not specifying one. If they did not specify a variant, and a previously used one does not exist, a default variant will be used.
    variant_to_use_for_current_command = ''
    variant_option_specified = (hasattr(Options.options, 'variant') and (Options.options.variant is not None))
    if variant_option_specified:
        variant_to_use_for_current_command = Options.options.variant
    else:
        # Default to using the most recently specified variant.
        most_recently_specified_variant_exists = option_values.variant is not None
        if most_recently_specified_variant_exists:
            variant_to_use_for_current_command = option_values.variant
        else:
            # Use a default variant.
            DEFAULT_VARIANT_NAME = 'default'
            variant_to_use_for_current_command = DEFAULT_VARIANT_NAME
    
    # STORE THE CURRENTLY SPECIFIED OPTIONS IN THE CACHE.
    # The cache will be created if it does not exist.
    option_values.variant = variant_to_use_for_current_command
    option_values.store(options_storage_path)
            
    # SET THE VARIANT OPTION FOR THE CURRENT COMMAND.
    # If this is a build command the variant will also be applied to the build context.
    Options.options.variant = variant_to_use_for_current_command
    BuildContext.variant = Options.options.variant

## Configures the build directory. In practice, this will configure options for a specific build variant that can be reused for all builds in that variant.
## \param[in]   conf - The configuration context.
def configure(conf):
    # LOAD CUSTOM PLUGINS AND COMMANDS.
    conf.load('Waf', tooldir = 'BuildFramework')
    
    # EXECUTE ANY CONFIGURATION COMMANDS NECESSARY FOR CUSTOM PLUGINS AND COMMANDS.
    conf.recurse(os.listdir(conf.path.abspath()), mandatory = False)
    
    # SET THE VARIANT TO USE FOR ALL BUILDS.
    conf.setenv(Options.options.variant)
    
    # STORE THE OPTIONS SPECIFIC TO THE CURRENT VARIANT.
    # This caches the options so they do not need to be specified on each build for this variant.
    conf.env.CPU = Options.options.cpu
    conf.env.OPTIMIZE = Options.options.optimize
    conf.env.SYMBOLS = Options.options.symbols
     
    # LOAD THE COMPILER.
    conf.load('compiler_cxx')

    # DETERMINE THE CURRENT PLATFORM.
    current_system_is_windows = ('win' in sys.platform)
    current_system_is_linux = ('linux' in sys.platform)
    
    # SET UP DEFINES TO MAKE IT EASY TO DELINEATE BETWEEN PLATFORM-SPECIFIC CODE.
    if current_system_is_windows:
        conf.env.append_value('DEFINES', 'WIN32')
    elif current_system_is_linux:
        conf.env.append_value('DEFINES', 'LINUX')
    else:
        raise WafError('Current platform not supported: %s' % sys.platform)
        
    # DETERMINE WHICH COMPILER IS BEING USED.
    using_gcc = ('gcc' == conf.env.CXX_NAME)
    using_visual_studio = ('msvc' == conf.env.CXX_NAME)
    using_clang = ('clang' == conf.env.CXX_NAME)
    compiler_supported = (using_gcc or using_visual_studio or using_clang)
    if not compiler_supported:
        raise WafError('C++ compiler not supported: %s' % conf.env.CXX_NAME)
        
    # CONFIGURE COMPILER OPTIONS.
    if using_gcc:
        # Load the GNU tool used to separate GCC symbols.
        conf.find_program('objcopy', var = 'OBJCOPY')

        # Enable C++17 features.
        conf.env.append_value('CXXFLAGS', '-std=c++17')

        # Enable stricter warnings. This encompasses a number of specific warnings for questionable code and 
        # common mistakes. See https://gcc.gnu.org/onlinedocs/gcc-4.8.5/gcc/Warning-Options.html for documentation.
        # Also consider adding -Wextra and -pedantic, and other flags suggested at 
        # https://lefticus.gitbooks.io/cpp-best-practices/content/02-Use_the_Tools_Available.html#gcc--clang.
        # \note C flags are provided, when applicable, as well as C++ flags because there is no C-specific waf code yet.
        conf.env.append_value('CFLAGS', '-Wall')
        conf.env.append_value('CXXFLAGS', '-Wall')

        # The following "-Wno-something" flags disable specific warnings that were enabled by -Wall:

        # Disable warnings for unused variables. This warning is generally useful, however it gets emitted for constants
        # defined in libraries for external use. These warnings are undesirable and obscure other warnings.
        conf.env.append_value('CFLAGS', '-Wno-unused-variable')
        conf.env.append_value('CXXFLAGS', '-Wno-unused-variable')

        # Disable warnings for unknown pragmas. Pragmas are generally not cross-platform, and certain pragmas in use are
        # for C++ analysis tools (not the compilers), so these warnings are undesirable and obscure other warnings. 
        conf.env.append_value('CFLAGS', '-Wno-unknown-pragmas')
        conf.env.append_value('CXXFLAGS', '-Wno-unknown-pragmas')

        # Older versions of gcc emit warnings about missing braces for array initializer lists even when their braces 
        # are correct. This warning is not included in -Wall for newer versions of gcc, so explicitly disable it for
        # consistent behavior across versions of gcc.
        conf.env.append_value('CFLAGS', '-Wno-missing-braces')
        conf.env.append_value('CXXFLAGS', '-Wno-missing-braces')

        # Warnings are emitted for certain characters appearing in comments. These warnings complain about harmless 
        # ASCII diagrams in our code.
        conf.env.append_value('CFLAGS', '-Wno-comment')
        conf.env.append_value('CXXFLAGS', '-Wno-comment')

        # Force "no return value" to be an error. C and C++ don't require a return statement, even
        # in functions that return non-void values. Behavior is undefined for functions (other
        # than main) that do this. This is described in sections 6.6.3/2 and 3.6.1/5 of the C++
        # standard. To help protect against undefined behavior, this is an error.
        # \note C flags are provided, when applicable, as well as C++ flags because there is no C-specific waf code yet.
        # See https://gcc.gnu.org/onlinedocs/gcc-4.8.5/gcc/Option-Summary.html#Option-Summary for documentation.
        conf.env.append_value('CFLAGS', '-Werror=return-type')
        conf.env.append_value('CXXFLAGS', '-Werror=return-type')

        # Use POSIX threads.
        conf.env.append_value('LINKFLAGS', '-pthread')

        # Enable POSIX real-time extensions such as asynchronous I/O and timers.
        conf.env.append_value('LIB', 'rt')

        # The dynamic linking API is required by some third party libraries at runtime. For example,
        # libcrypto.
        conf.env.append_value('LIB', 'dl')

        # Configure optimizations.
        if conf.env.OPTIMIZE:
            conf.env.append_value('CFLAGS', '-O2')
            conf.env.append_value('CXXFLAGS', '-O2')
        else:
            conf.env.append_value('CFLAGS', '-O0')
            conf.env.append_value('CXXFLAGS', '-O0')

        # Configure debugging symbols.
        if conf.env.SYMBOLS:
            conf.env.append_value('CFLAGS', '-g')
            conf.env.append_value('CXXFLAGS', '-g')

    elif using_visual_studio:
        # Use C++ 17 features.
        conf.env.append_value('CXXFLAGS', '/std:c++17')
        
        # Enable stricter warnings for C++ code.
        # The flag is not applied to C code yet because any C warnings will come from third-party
        # code, and generally those warnings are not considered to be as important, and could 
        # obscure more important warnings from our own code. /W3 displays "production quality" warnings,
        # while /W2 displays "severe" and "significant" warnings, and the default (/W1) only shows 
        # "severe" warnings. See https://msdn.microsoft.com/en-us/library/thxezb7y.aspx for documentation.
        conf.env.append_value('CXXFLAGS', '/W3')

        # Visual Studio min/max macros conflict with the C++ standard library.
        conf.env.append_value('DEFINES', 'NOMINMAX')

        if ('x86' == conf.env.CPU):
            # Instruct the linker to create a console program that can run on 32-bit Windows XP.
            conf.env.append_value('LINKFLAGS', '/SUBSYSTEM:CONSOLE,5.01')
        elif ('x64' == conf.env.CPU):
            # A preprocessor define is needed for intellisense to correctly handle
            # architecture-specific #ifdef's.
            conf.env.append_value('DEFINES', '_WIN64')
            conf.env.append_value('DEFINES', '_M_X64')

        # Enable all exceptions.
        conf.env.append_value('CXXFLAGS', '/EHa')

        # Increase the number of sections object files can contain.
        # By default, object files can only have 2^16 sections, but /bigobj increases that limit up to 2^32.
        # The only known penalty with using /bigobj is that it prevents linkers prior to Visual Studio 2005
        # from reading the generated object files.
        # \note C flags are provided, when applicable, as well as C++ flags because there is no C-specific waf code yet.
        # See https://msdn.microsoft.com/en-us/library/fwkeyyhe.aspx for documentation.
        conf.env.append_value('CFLAGS', '/bigobj')
        conf.env.append_value('CXXFLAGS', '/bigobj')

        # Globally link to the multithread, static version of the runtime library.
        if conf.env.OPTIMIZE:
            conf.env.append_value('CFLAGS', '/MT')
            conf.env.append_value('CXXFLAGS', '/MT')
        else:
            conf.env.append_value('CFLAGS', '/MTd')
            conf.env.append_value('CXXFLAGS', '/MTd')

            # The preprocessor "_DEBUG" is automatically defined by the compiler when /MTd is
            # specified (see msdn.microsoft.com/en-us/library/0b98s6w8.aspx). It should be added
            # explicitly for intellisense to correctly display #ifdef's that use this preprocessor.
            conf.env.append_value('DEFINES', '_DEBUG')

        # Globally link to all needed windows libraries.
        conf.env.append_value('LINKFLAGS', 'OpenGL32.lib')
        conf.env.append_value('LINKFLAGS', 'gdi32.lib')
        conf.env.append_value('LINKFLAGS', 'Winmm.lib')
        conf.env.append_value('LINKFLAGS', 'Advapi32.lib')
        conf.env.append_value('LINKFLAGS', 'crypt32.lib')
        conf.env.append_value('LINKFLAGS', 'shell32.lib')
        conf.env.append_value('LINKFLAGS', 'psapi.lib')
        conf.env.append_value('LINKFLAGS', 'iphlpapi.lib')
        conf.env.append_value('LINKFLAGS', 'wbemuuid.lib')
        conf.env.append_value('LINKFLAGS', 'Setupapi.lib')
        conf.env.append_value('LINKFLAGS', 'Winmm.lib')
        conf.env.append_value('LINKFLAGS', 'Winspool.lib')
        conf.env.append_value('LINKFLAGS', 'ws2_32.lib')
        conf.env.append_value('LINKFLAGS', 'Comctl32.lib')
        conf.env.append_value('LINKFLAGS', 'Comdlg32.lib')
        conf.env.append_value('LINKFLAGS', 'Windowscodecs.lib')
        conf.env.append_value('LINKFLAGS', 'UxTheme.lib')
        conf.env.append_value('LINKFLAGS', 'User32.lib')
        conf.env.append_value('LINKFLAGS', 'kernel32.lib')

        # Configure optimizations.
        if conf.env.OPTIMIZE:
            conf.env.append_value('CFLAGS', '/O2')
            conf.env.append_value('CXXFLAGS', '/O2')

            # The optimizations /OPT:REF and /OPT:ICF are enabled by default in non-debug builds,
            # but are disabled by default in debug builds. They're explicitly set here to control
            # optimizations regardless of the debug status. Their usage prevents incremental linking
            # but the /INCREMENTAL:NO flag is specified for completeness.
            conf.env.append_value(
                'LINKFLAGS',
                ['/OPT:REF', '/OPT:ICF', '/INCREMENTAL:NO'])
        else:
            conf.env.append_value('CFLAGS', '/Od')
            conf.env.append_value('CXXFLAGS', '/Od')

        # Configure debugging symbols.
        if conf.env.SYMBOLS:
            # OUTPUT LIBRARIES WITH EMBEDDED SYMBOLS.
            # Embedded symbols make the static libraries easier to manage.
            conf.env.append_value('CFLAGS', ['/DEBUG', '/Z7'])
            conf.env.append_value('CXXFLAGS', ['/DEBUG', '/Z7'])

            # OUTPUT EXECUTABLES WITH EXTERNAL SYMBOLS.
            # Symbols are separated so they can be excluded from the final product.
            conf.env.append_value(
                'LINKFLAGS',
                ['/DEBUG', '/MAP', '/MAPINFO:EXPORTS'])
    
def build(bld):
    # CHECK FOR MISSPELLED TARGETS AND OFFER SUGGESTIONS.
    bld.load('Waf', tooldir = 'BuildFramework')
    from Waf.Utilities import GetTargetProjects
    bld.add_pre_fun(GetTargetProjects)
    
    # PRINT THE CURRENT SETTINGS USED FOR THIS BUILD.
    from Waf.Utilities import PrintWafSettings
    bld.add_pre_fun(PrintWafSettings)
    
    # RECUSE INTO SUB-DIRECTORIES TO FIND BUILD TARGETS.
    bld.recurse(os.listdir(bld.path.abspath()), mandatory=False)
    