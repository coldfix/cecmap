import cec

import os
import signal
import subprocess
from enum import Enum


class Mode(Enum):
    Keyboard = 0


class Event(Enum):
    KeyDown = 0
    KeyUp = 1


class Keycode(Enum):
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


def run(*args, **kwargs):
    return subprocess.Popen(args, **kwargs)


def xdo(*args):
    return run("xdotool", *[str(arg) for arg in args])


KEYBINDINGS = {
    (Mode.Keyboard, Event.KeyDown): {
        Keycode.Up:     (xdo, "keydown", "Up"),
        Keycode.Down:   (xdo, "keydown", "Down"),
        Keycode.Left:   (xdo, "keydown", "Left"),
        Keycode.Right:  (xdo, "keydown", "Right"),
        Keycode.Ok:     (xdo, "keydown", "Return"),
        Keycode.Play:   (xdo, "keydown", "XF86AudioPlay"),
        Keycode.Pause:  (xdo, "keydown", "XF86AudioPause"),
        Keycode.Back:   (xdo, "keydown", "Escape"),
        Keycode.Red:    (xdo, "keydown", "Super_L"),
        Keycode.Green:  (run, "kodi"),
        Keycode.Blue:   (run, "chromium-browser"),
    },
    (Mode.Keyboard, Event.KeyUp): {
        Keycode.Up:     (xdo, "keyup", "Up"),
        Keycode.Down:   (xdo, "keyup", "Down"),
        Keycode.Left:   (xdo, "keyup", "Left"),
        Keycode.Right:  (xdo, "keyup", "Right"),
        Keycode.Ok:     (xdo, "keyup", "Return"),
        Keycode.Play:   (xdo, "keyup", "XF86AudioPlay"),
        Keycode.Pause:  (xdo, "keyup", "XF86AudioPause"),
        Keycode.Back:   (xdo, "keyup", "Escape"),
        Keycode.Red:    (xdo, "keyup", "Super_L"),
        # Keycode.Green:  (run, "kodi"),
        # Keycode.Blue:   (run, "chromium-browser"),
    },
}


class Condition:

    def __init__(self, **attrs):
        self.attrs = attrs

    def __and__(self, other):
        return Condition(**{**self.attrs, **other.attrs})

    def check(self, **attrs):
        return all([
            self.attrs[key] == val
            for key, val in attrs.items()
            if key in self.attrs
        ])


def make_condition(on):
    if not isinstance(on, (tuple, list)):
        on = [on]
    return Condition(**{
        x.__class__.__name__.lower(): x.value
        for x in on
    })


def make_keybindings(on, action):
    cond = make_condition(on)
    if isinstance(action, dict):
        return [
            (cond & x_cond, x_do)
            for x in action.items()
            for x_cond, x_do in make_keybindings(*x)
        ]
    else:
        return [(cond, action)]


def main():
    print("Initializing...")
    os.environ.setdefault('DISPLAY', ':0')
    client = Client(num_modes=len(Mode.__members__))
    client.bind(KEYBINDINGS)
    client.connect()
    print("Ready")
    signal.pause()


class Client:

    def __init__(self, *, num_modes=2):
        self.keybindings = []
        self.num_modes = num_modes
        self.mode = 0
        self.bind({(Keycode.Yellow, Event.KeyDown): [self.switch_mode]})

    def bind(self, rules):
        self.keybindings.extend(make_keybindings((), rules))

    def switch_mode(self, mode=None):
        if mode is None:
            mode = self.mode + 1
        self.mode = mode % self.num_modes

    def connect(self):
        cec.init()
        cec.set_active_source()
        cec.add_callback(self.on_keypress, cec.EVENT_KEYPRESS)

    def on_keypress(self, event, keycode, duration):
        mode = self.mode
        event = (Event.KeyDown if duration == 0 else Event.KeyUp).value
        for on, action in self.keybindings:
            if on.check(keycode=keycode, mode=mode, event=event):
                func, *args = action
                func(*args)
                break


if __name__ == '__main__':
    main()
