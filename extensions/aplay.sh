#!/bin/bash

# When playing audio on a large display (like a TV) you generally want
# something full screen indicating what you're playing. This lets you play
# music in mplayer with the usual controls.

for i in convert ffmpeg mplayer; do
    which ${i} &>/dev/null
    if [ $? -ne 0 ]; then
        echo "${i} not found" >&2
        exit 1
    fi
done

if [ $# -ne 1 ]; then
    echo "Usage: $0 file" >&2
    exit 1
fi

TEMP=`mktemp -d`
trap 'rm -rf "${TEMP}"; exit' EXIT INT TERM QUIT

HEIGHT=1080
WIDTH=1920

convert -size ${WIDTH}x${HEIGHT} xc:black -pointsize 48 -fill white -draw "gravity Center text 0,0 \"$1\"" "${TEMP}/black.png"
ffmpeg -loop 1 -i "${TEMP}/black.png" -i "$1" -acodec copy -shortest -f mpegts - | mplayer -fs -cache-min 0 -
