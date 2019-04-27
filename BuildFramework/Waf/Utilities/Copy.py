from __future__ import absolute_import, division, print_function

import shutil

from waflib import Logs
from waflib.Configure import conf

## \package Waf.Utilities.Copy
## This package provides an interface for copying files as part of a build.
## Each source and target must be a complete filename or waf file node (not just a directory).
## The first source will be copied to the first target and so on.
## The following example shows how to use the feature.
## \code
##
##    bld.copy(
##        source = ['SourceFile.in', 'SourceFile2.in'],
##        target = ['TargetFile.out', 'TargetFile2.out'],
##        name = 'CopyExample')
##
## \endcode

## Sets the 'copy' alias so that the user can create copying tasks using the bld.copy interface.
@conf
def copy(bld, *k, **kw):
    # SET THE RULE FOR COPYING THE FILES.
    kw['rule'] = CopyFiles
    return bld(*k, **kw)

## Copies the files specified by the inputs of a task to the corresponding output locations.
## \param[in,out] task - The task, which should have an equal number of inputs and outputs.
## \returns - 0 if the task finished normally, or 1 otherwise.
def CopyFiles(task):
    # Verify that an equal number of inputs and outputs were specified.
    input_and_output_count_are_equal = (len(task.inputs) == len(task.outputs))
    if not input_and_output_count_are_equal:
        Logs.error('Number of sources must equal number of targets')
        return 1

    # Copy the file at each input path to the corresponding output path.
    for pair in zip(task.inputs, task.outputs):
        shutil.copyfile(
            pair[0].abspath(),
            pair[1].abspath())
    return 0
