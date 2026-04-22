#!/usr/bin/env bash
set -euo pipefail

cd /boot/firmware/splash

for i in 1 2 3 4 5 6; do
  ffmpeg -y \
    -i "${i}-left.mp4" \
    -i "${i}-right.mp4" \
    -filter_complex "[0:v]fps=30,scale=1280:720,setsar=1[left];[1:v]fps=30,scale=1280:720,setsar=1[right];[left][right]hstack=inputs=2[v]" \
    -map "[v]" \
    -an \
    -c:v libx264 \
    -preset veryfast \
    -crf 23 \
    -pix_fmt yuv420p \
    -r 30 \
    "${i}.mp4"
done
