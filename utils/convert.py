import os
from subprocess import Popen, PIPE
from ftransc.utils.constants import (
        EXTERNAL_FORMATS, 
        EXTERNAL_ENCODERS, 
        EXTERNAL_ENCODER_OUTPUT_OPT,
        FFMPEG_AVCONV
        )


def convert(infilename, audioformat, outputfolder=None, audiopresets=None, logfile=None, external_enc=False):
    if outputfolder in (None, ''):
        outputfolder = "./"
    if logfile is None:
        logfile = open("/dev/null", 'w')

    audioformat = audioformat.lower()
    basefilename, ext = os.path.splitext(infilename)
    outfilename = outputfolder + '/' + basefilename + '.' + audioformat
    utility = _get_external_encoder(audioformat)

    cmdline = [FFMPEG_AVCONV, '-y', '-i']
    cmdline += [infilename]

    if utility not in (None, '') and (external_enc or audioformat in EXTERNAL_FORMATS):
        output_opt = EXTERNAL_ENCODER_OUTPUT_OPT.get(utility, '')
        cmdline += "-f wav /dev/stdout".split()
        if output_opt:
            cmdline2 = [utility] + audiopresets.split() + ["-", output_opt, outfilename]
        else:
            cmdline2 = [utility] + audiopresets.split() + ["-", outfilename]

        pipeline1 = Popen(cmdline, stdout=PIPE, stderr=logfile)
        pipeline = Popen(cmdline2, stdin=pipeline1.stdout,stdout=PIPE, stderr=logfile)
    else:
        if audiopresets is not None:
            cmdline += audiopresets.split()
        cmdline += [outfilename]
        pipeline = Popen(cmdline, stdout=PIPE, stderr=logfile)

    pipeline.communicate()
    return pipeline.returncode == 0


def _get_external_encoder(audioformat):
    return EXTERNAL_ENCODERS.get(audioformat)

