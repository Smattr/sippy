#!/bin/bash

# VCD tracks often come as a pair of a BIN file and a CUE file. Mplayer's
# naïve attempt to play a BIN file usually picks the wrong track and you'll end
# up with no audio or the video timings off. This script passes mplayer the
# correct argument to tell it to read the timings from the CUE file.

if [ $# -lt 1 ]; then
    echo "Usage: $0 file mplayer_options..." >&2
    exit 1
fi

which mplayer &>/dev/null
if [ $? -ne 0 ]; then
    echo "mplayer not found" >&2
    exit 1
fi

FILENAME=`echo "$1" | \
    sed -e 's/\.b\(..\)$/.c\1/g' \
        -e 's/\.B\(..\)$/.C\1/g' \
        -e 's/\.\(.\)i\(.\)$/.\1u\2/g' \
        -e 's/\.\(.\)I\(.\)$/.\1U\2/g' \
        -e 's/\.\(..\)n$/.\1e/g' \
        -e 's/\.\(..\)N$/.\1E/g'`
shift

mplayer "$@" "cue://${FILENAME}:2"
