import cec

import os
import signal
import subprocess
from functools import partial


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


def Run(*args, **kwargs):
    return partial(subprocess.Popen, [args], **kwargs)


def Xdo(*args):
    return Run(["xdotool"] + [str(arg) for arg in args])


KEYBINDINGS = {
    Keycode.Up:      Xdo("key", "Up"),
    Keycode.Down:    Xdo("key", "Down"),
    Keycode.Left:    Xdo("key", "Left"),
    Keycode.Right:   Xdo("key", "Right"),
    Keycode.Ok:      Xdo("key", "Return"),
    Keycode.Back:    Xdo("key", "Escape"),
    Keycode.Red:     Xdo("key", "Super_L"),
    Keycode.Green:   Run("kodi"),
    Keycode.Blue:    Run("chromium-browser"),
    Keycode.Yellow:  Run("shutdown", "-h", "now"),
}


def main():
    print("Initializing...")
    os.environ.setdefault('DISPLAY', ':0')
    client = Client()
    client.keybindings = KEYBINDINGS
    client.connect()
    print("Ready")
    signal.pause()


class Client:

    def __init__(self):
        self.keybindings = {}

    def connect(self):
        cec.init()
        cec.set_active_source()
        cec.add_callback(self.on_keypress, cec.EVENT_KEYPRESS)

    def on_keypress(self, event, keycode, duration):
        if duration != 0:
            action = self.keybindings.get(keycode)
            if action:
                action()


if __name__ == '__main__':
    main()
