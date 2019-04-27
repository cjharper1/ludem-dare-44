from __future__ import absolute_import, division, print_function

import re
import sys

from waflib import Logs

## \package Waf.Utilities.CustomLogFormatter
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

## This is called whenever waf is run, before a command context is initialized. 
## Here, it installs the color log formatter.
## \param[in] options_context - The options context. This is unused.
def options(options_context):
    # INSTALL THE FORMATTER.
    Logs.log.handlers[0].setFormatter(CustomLogFormatter())
