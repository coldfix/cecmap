import cec

import os
import signal
from time import sleep
from subprocess import run


class Keycode:
    Up = 1
    Down = 2
    Left = 3
    Right = 4

    Ok = 0
    Back = 13

    Red = 114
    Green = 115
    Yellow = 116
    Blue = 113

    Play = 68
    Pause = 70


def main():
    print("Initializing...")
    os.environ.setdefault('DISPLAY', ':0')
    cec.init()
    cec.set_active_source()
    cec.add_callback(on_keypress, cec.EVENT_KEYPRESS)
    print("Ready")
    signal.pause()


def on_keypress(event, keycode, duration):
    if duration != 0:
        if keycode == Keycode.Up:
            xdo("key", "Up")
        elif keycode == Keycode.Down:
            xdo("key", "Down")
        elif keycode == Keycode.Left:
            xdo("key", "Left")
        elif keycode == Keycode.Right:
            xdo("key", "Right")

        elif keycode == Keycode.Ok:
            xdo("key", "Return")
        elif keycode == Keycode.Back:
            xdo("key", "Escape")

        elif keycode == Keycode.Red:
            xdo("key", "Super_L")
        elif keycode == Keycode.Green:
            run(["kodi"])
        elif keycode == Keycode.Blue:
            run(["chromium-browser"])
        elif keycode == Keycode.Yellow:
            run(["shutdown", "-h", "now"])


def xdo(*args):
    run(["xdotool"] + [str(arg) for arg in args])


if __name__ == '__main__':
    main()
