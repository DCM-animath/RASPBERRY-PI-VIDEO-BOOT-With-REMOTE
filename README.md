# RASPBERRY PI VIDEO BOOT With REMOTE

Sistem Raspberry Pi dual HDMI dengan 1 MPV untuk video gabungan 2560x720.

## Layout layar

- HDMI-A-2 di kiri, posisi 0,0
- HDMI-A-1 di kanan, posisi 1280,0
- Video final: 2560x720
- Bagian kiri video 1280x720 tampil di HDMI-A-2
- Bagian kanan video 1280x720 tampil di HDMI-A-1

## File video

Letakkan file berikut di `/boot/firmware/splash/`:

```text
1.mp4 = idle, loop terus
2.mp4 = GPIO17
3.mp4 = GPIO27
4.mp4 = GPIO22
5.mp4 = GPIO23
6.mp4 = GPIO24
```

## Format video yang disarankan
- Buat video berukuran 2 monitor 
- Resolusi: 2560x720
- FPS: 30 fps constant
- Codec: H.264
- Pixel format: yuv420p
- Audio: tidak perlu

## Install dari GitHub

```bash
curl -fsSL https://raw.githubusercontent.com/DCM-animath/raspi-dual-mpv/main/install.sh | sudo bash
```

## Cek status

```bash
sudo systemctl status dualmp4.service --no-pager -l
sudo systemctl status dualgpio.service --no-pager -l
pgrep -af mpv
```

## Cek log tombol

```bash
sudo journalctl -u dualgpio.service -f
```

## Pindahkan video dari home/pi

```bash
sudo mv /home/pi/1.mp4 /home/pi/2.mp4 /home/pi/3.mp4 /home/pi/4.mp4 /home/pi/5.mp4 /home/pi/6.mp4 /boot/firmware/splash/
```

## Jika masih memakai file lama left/right

Jalankan:

```bash
sudo bash /boot/firmware/splash/combine_pairs.sh
```

Script itu akan membuat:

```text
1.mp4
2.mp4
3.mp4
4.mp4
5.mp4
6.mp4
```
