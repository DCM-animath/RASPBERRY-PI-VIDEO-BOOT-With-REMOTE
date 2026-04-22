#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/DCM-animath/raspi-dual-mpv.git"
APP_DIR="/opt/raspi-dual-mpv"

if [[ $EUID -ne 0 ]]; then
  echo "Jalankan script ini dengan sudo."
  exit 1
fi

apt-get update
apt-get install -y git mpv ffmpeg python3-libgpiod rsync wlr-randr

rm -rf "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"

rsync -a "$APP_DIR/root/" /

chmod +x /boot/firmware/splash/start_dual.sh || true
chmod +x /boot/firmware/splash/gpio_switch.py || true
chmod +x /boot/firmware/splash/combine_pairs.sh || true

systemctl daemon-reload
systemctl disable --now mpvsync.service >/dev/null 2>&1 || true
systemctl enable dualmp4.service
systemctl enable dualgpio.service
systemctl restart dualmp4.service || true
systemctl restart dualgpio.service || true

echo "Instalasi selesai."
echo "Letakkan video di /boot/firmware/splash/1.mp4 sampai 6.mp4"
echo "Cek status: sudo systemctl status dualmp4.service dualgpio.service --no-pager -l"
