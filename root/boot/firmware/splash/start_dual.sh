#!/usr/bin/env bash
set -euo pipefail

export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

SOCK="/tmp/mpv-main.sock"

pkill -f "mpv.*mpv-main.sock" 2>/dev/null || true
rm -f "$SOCK"

echo "[INFO] tunggu runtime Wayland..."

while [ ! -d /run/user/1000 ]; do
  sleep 1
done

while [ ! -S /run/user/1000/wayland-0 ]; do
  sleep 1
done

echo "[INFO] Wayland siap. Start 1 mpv 2560x720..."

exec /usr/bin/mpv \
  --no-config \
  --no-terminal \
  --no-audio \
  --idle=yes \
  --keep-open=yes \
  --force-window=yes \
  --border=no \
  --ontop \
  --geometry=2560x720+0+0 \
  --autofit-larger=2560x720 \
  --no-osc \
  --no-osd-bar \
  --hwdec=auto-safe \
  --vo=gpu \
  --gpu-context=wayland \
  --profile=fast \
  --input-ipc-server="$SOCK"
