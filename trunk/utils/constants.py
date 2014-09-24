#!/usr/bin/python
from subprocess import PIPE, Popen

def _determine_ffmpeg_utility():
    avutil = None
    for util in ["avconv", "ffmpeg"]:
        found = Popen(["which", util], stdout=PIPE).communicate()[0].strip()
        if found:
            avutil = util
            break
    if avutil is None:
        raise SystemExit("ffmpeg/avconv not installed")
    return avutil


NO_TAGS             = False
SILENT              = False  
VERSION             = '5.1.3'
LOGFILE             = '/dev/null'
SUPPORTED_FORMATS   = set(['mp3', 'wma', 'wav', 'ogg', 'flac', 'm4a', 'mpc', 'wv', 'avi'])
EXTERNAL_FORMATS    = set(["mpc", "wv"])
INTERNAL_FORMATS    = SUPPORTED_FORMATS - EXTERNAL_FORMATS
EXTERNAL_ENCODERS   = {
    "mpc"   : "mppenc",
    "wv"    : "wavpack",
    "mp3"   : "lame",
    "ogg"   : "oggenc",
    "m4a"   : "faac",
    "flac"  : "flac",
}
EXTERNAL_ENCODER_OUTPUT_OPT = {
    'mppenc'    : '',
    'lame'      : '',
    'faac'      : '-o',
    'flac'      : '-o',
    'oggenc'    : '-o',
    'wavpack'   : '-o',
}

FFMPEG_AVCONV = _determine_ffmpeg_utility()

DEPENDENCIES = {
    'cdparanoia'        : [],
    FFMPEG_AVCONV       : list(SUPPORTED_FORMATS),
    }
for audio_format, encoder in EXTERNAL_ENCODERS.iteritems():
    DEPENDENCIES[encoder] = [audio_format]

