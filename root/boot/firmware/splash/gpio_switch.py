#!/usr/bin/env python3
import json
import os
import socket
import sys
import time
import signal
from datetime import timedelta

import gpiod
from gpiod.line import Direction, Bias, Value

MPV_SOCK = "/tmp/mpv-main.sock"

IDLE_SET = 1
SOCKET_WAIT_TIMEOUT = 30

SAMPLE_INTERVAL = 0.02
STABLE_SAMPLES = 3

BOOT_IGNORE_SECONDS = 1.0
RELEASE_STABLE_SECONDS = 0.30

RETURN_MARGIN = 0.18

FILES = {
    1: "/boot/firmware/splash/1.mp4",
    2: "/boot/firmware/splash/2.mp4",
    3: "/boot/firmware/splash/3.mp4",
    4: "/boot/firmware/splash/4.mp4",
    5: "/boot/firmware/splash/5.mp4",
    6: "/boot/firmware/splash/6.mp4",
}

BUTTON_TO_SET = {
    17: 2,
    27: 3,
    22: 4,
    23: 5,
    24: 6,
}

BUTTONS = list(BUTTON_TO_SET.keys())

current_mode = "idle"
current_set = IDLE_SET


def cleanup(*_):
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


def find_chip_path():
    for path in ("/dev/gpiochip4", "/dev/gpiochip0"):
        if os.path.exists(path):
            print(f"[INFO] pakai GPIO chip: {path}", flush=True)
            return path
    raise FileNotFoundError("GPIO chip tidak ditemukan")


def wait_for_socket():
    deadline = time.time() + SOCKET_WAIT_TIMEOUT
    while time.time() < deadline:
        if os.path.exists(MPV_SOCK):
            print("[INFO] socket mpv siap", flush=True)
            return
        time.sleep(0.2)
    raise TimeoutError("socket mpv belum muncul")


def mpv_cmd(command):
    payload = json.dumps({"command": command}) + "\n"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect(MPV_SOCK)
        s.sendall(payload.encode("utf-8"))
        try:
            data = s.recv(4096)
            if data:
                return json.loads(data.decode("utf-8", errors="ignore"))
        except Exception:
            return None
    finally:
        try:
            s.close()
        except Exception:
            pass
    return None


def get_prop(prop):
    resp = mpv_cmd(["get_property", prop])
    if isinstance(resp, dict):
        return resp.get("data")
    return None


def set_prop(prop, value):
    mpv_cmd(["set_property", prop, value])


def load_file(set_num, loop_forever):
    global current_mode, current_set

    path = FILES[set_num]

    if not os.path.exists(path):
        print(f"[WARN] file tidak ada: {path}", flush=True)
        return False

    set_prop("pause", True)
    set_prop("loop-file", "inf" if loop_forever else "no")
    mpv_cmd(["loadfile", path, "replace"])

    deadline = time.time() + 2.5
    while time.time() < deadline:
        cur = get_prop("path")
        dur = get_prop("duration")
        if cur == path and dur is not None:
            break
        time.sleep(0.02)

    set_prop("pause", False)

    current_set = set_num
    current_mode = "idle" if loop_forever else "oneshot"

    mode = "IDLE" if loop_forever else "ONESHOT"
    print(f"[INFO] set {set_num} -> {os.path.basename(path)} | {mode}", flush=True)
    return True


def get_pressed_pins(request):
    active = []
    for pin in BUTTONS:
        val = request.get_value(pin)
        if val is Value.INACTIVE:
            active.append(pin)
    return active


def read_single_pressed(request):
    active = get_pressed_pins(request)
    if len(active) == 1:
        return active[0]
    return None


def wait_boot_release(request):
    print("[INFO] warmup boot...", flush=True)
    time.sleep(BOOT_IGNORE_SECONDS)

    need_samples = max(1, int(RELEASE_STABLE_SECONDS / SAMPLE_INTERVAL))
    stable_release = 0

    print("[INFO] menunggu semua tombol release stabil...", flush=True)

    while True:
        active = get_pressed_pins(request)

        if len(active) == 0:
            stable_release += 1
        else:
            stable_release = 0
            print(f"[INFO] tombol masih aktif saat boot: {active}", flush=True)

        if stable_release >= need_samples:
            print("[INFO] semua tombol release. input siap.", flush=True)
            return

        time.sleep(SAMPLE_INTERVAL)


def oneshot_finished():
    idle_active = get_prop("idle-active")
    if idle_active is True:
        return True

    pos = get_prop("playback-time")
    dur = get_prop("duration")

    if pos is None or dur is None:
        return False

    pos = float(pos)
    dur = float(dur)

    return pos >= (dur - RETURN_MARGIN)


def main():
    global current_mode

    chip_path = find_chip_path()
    wait_for_socket()

    config = {
        pin: gpiod.LineSettings(
            direction=Direction.INPUT,
            bias=Bias.PULL_UP,
            debounce_period=timedelta(milliseconds=10),
        )
        for pin in BUTTONS
    }

    last_sample = None
    stable_count = 0
    handled_pin = None

    with gpiod.request_lines(
        chip_path,
        consumer="single-mpv-gpio",
        config=config,
    ) as request:
        print("[INFO] GPIO watcher aktif", flush=True)

        if not load_file(IDLE_SET, loop_forever=True):
            raise RuntimeError("gagal load idle")

        wait_boot_release(request)

        while True:
            pin = read_single_pressed(request)

            if pin == last_sample:
                stable_count += 1
            else:
                last_sample = pin
                stable_count = 1

            if pin is None:
                handled_pin = None

            elif stable_count >= STABLE_SAMPLES and handled_pin != pin:
                target_set = BUTTON_TO_SET[pin]
                print(f"[DEBUG] pin terbaca GPIO{pin} -> set {target_set}", flush=True)
                load_file(target_set, loop_forever=False)
                handled_pin = pin

            if current_mode == "oneshot" and oneshot_finished():
                load_file(IDLE_SET, loop_forever=True)

            time.sleep(SAMPLE_INTERVAL)


if __name__ == "__main__":
    main()
