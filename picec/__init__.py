#! /usr/bin/env python
import cec

import os
import subprocess
import time
from enum import Enum
from queue import Queue, Empty


class Mode(Enum):
    Mouse = 0
    Keyboard = 1


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


def launch(*args, **kwargs):
    return subprocess.Popen(args, preexec_fn=os.setpgrgp, **kwargs)


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


class Cursor:

    def __init__(self, mouse):
        self.mouse = mouse
        self.active = set()
        self.dx = {Keycode.Left: -1, Keycode.Right: 1}
        self.dy = {Keycode.Up: -1, Keycode.Down: 1}
        self.pos0 = (0, 0)
        self.pos1 = self.pos0

    def move(self, key):
        self.active.add(key)

    def stop(self, key):
        self.active.remove(key)

    def dispatch(self, delta):
        if self.active:
            dx = sum([self.dx.get(key, 0) for key in self.active])
            dy = sum([self.dy.get(key, 0) for key in self.active])
            x0, y0 = self.pos0
            x1, y1 = self.pos1
            x1 += dx * delta
            y1 += dy * delta
            x2 = round(x1)
            y2 = round(y1)
            self.pos0 = (x2, y2)
            self.pos1 = (x1, y1)
            if x2 != x0 or y2 != y0:
                self.mouse.move(x2 - x0, y2 - y0)


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


class Clock:

    def __init__(self):
        self.prev = time.perf_counter()

    def __call__(self):
        now = time.perf_counter()
        delta = now - self.prev
        self.prev = now
        return delta


def main():
    print("Initializing...")
    os.environ.setdefault('DISPLAY', ':0')
    from pynput.mouse import Controller as Mouse, Button
    from pynput.keyboard import Controller as Keyboard, Key
    mouse = Mouse()
    keyboard = Keyboard()

    timestep = 0.01
    mouse_speed = 200

    cursor = Cursor(mouse)
    client = Client(num_modes=len(Mode.__members__))
    client.bind({
        (Mode.Keyboard, Event.KeyDown): {
            Keycode.Up:     (keyboard.press, Key.up),
            Keycode.Down:   (keyboard.press, Key.down),
            Keycode.Left:   (keyboard.press, Key.left),
            Keycode.Right:  (keyboard.press, Key.right),
            Keycode.Ok:     (keyboard.press, Key.enter),
            Keycode.Play:   (keyboard.press, Key.media_play_pause),
            Keycode.Pause:  (keyboard.press, Key.media_play_pause),
            Keycode.Back:   (keyboard.press, Key.esc),
            Keycode.Red:    (keyboard.press, Key.cmd),
            Keycode.Green:  (launch, "kodi"),
            Keycode.Blue:   (launch, "chromium-browser"),
        },
        (Mode.Keyboard, Event.KeyUp): {
            Keycode.Up:     (keyboard.release, Key.up),
            Keycode.Down:   (keyboard.release, Key.down),
            Keycode.Left:   (keyboard.release, Key.left),
            Keycode.Right:  (keyboard.release, Key.right),
            Keycode.Ok:     (keyboard.release, Key.enter),
            Keycode.Play:   (keyboard.release, Key.media_play_pause),
            Keycode.Pause:  (keyboard.release, Key.media_play_pause),
            Keycode.Back:   (keyboard.release, Key.esc),
            Keycode.Red:    (keyboard.release, Key.cmd),
            # Keycode.Green:  (launch, "kodi"),
            # Keycode.Blue:   (launch, "chromium-browser"),
        },
        (Mode.Mouse, Event.KeyDown): {
            Keycode.Up:     (cursor.move, Keycode.Up),
            Keycode.Down:   (cursor.move, Keycode.Down),
            Keycode.Left:   (cursor.move, Keycode.Left),
            Keycode.Right:  (cursor.move, Keycode.Right),
            Keycode.Ok:     (mouse.press, Button.left),
            Keycode.Play:   (mouse.press, Button.middle),
            Keycode.Pause:  (mouse.press, Button.right),
            Keycode.Back:   (keyboard.press, Key.esc),
            Keycode.Red:    (keyboard.press, Key.cmd),
            Keycode.Green:  (mouse.scroll, 0, +1),
            Keycode.Blue:   (mouse.scroll, 0, -1),
        },
        (Mode.Mouse, Event.KeyUp): {
            Keycode.Up:     (cursor.stop, Keycode.Up),
            Keycode.Down:   (cursor.stop, Keycode.Down),
            Keycode.Left:   (cursor.stop, Keycode.Left),
            Keycode.Right:  (cursor.stop, Keycode.Right),
            Keycode.Ok:     (mouse.release, Button.left),
            Keycode.Play:   (mouse.release, Button.middle),
            Keycode.Pause:  (mouse.release, Button.right),
            Keycode.Back:   (keyboard.release, Key.esc),
            Keycode.Red:    (keyboard.release, Key.cmd),
            # Keycode.Green:  (mouse.scroll, 0, +1),
            # Keycode.Blue:   (mouse.scroll, 0, -1),
        },
    })
    client.connect()
    print("Ready")

    clock = Clock()
    while True:
        timeout = timestep if cursor.active else None
        events = client.recv(timeout)
        time_delta = clock()
        cursor.dispatch(time_delta * mouse_speed)
        for event in events:
            client.dispatch(*event)


class Client:

    def __init__(self, *, num_modes=2):
        self.keybindings = []
        self.num_modes = num_modes
        self.mode = 0
        self.bind({(Keycode.Yellow, Event.KeyDown): [self.switch_mode]})
        self.events = Queue()

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
        self.events.put((event, keycode, duration))

    def recv(self, timeout):
        events = []
        try:
            events.append(self.events.get(timeout=timeout))
            while True:
                events.append(self.events.get_nowait())
        except Empty:
            return events

    def dispatch(self, event, keycode, duration):
        mode = self.mode
        event = (Event.KeyDown if duration == 0 else Event.KeyUp).value
        for on, action in self.keybindings:
            if on.check(keycode=keycode, mode=mode, event=event):
                func, *args = action
                func(*args)
                break


if __name__ == '__main__':
    main()
