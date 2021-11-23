"""
2-mode configuration for LG with MagicRemote.
"""

from enum import Enum
from picec import launch, Event
from picec.device import Key, Button, Keyboard, Mouse


class Mode(Enum):
    Mouse = 0
    Keyboard = 1


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


def setup(client):
    mouse = Mouse()
    keyboard = Keyboard()

    client.num_modes = 2
    client.switch_mode(Mode.Mouse)
    client.add_device(mouse)
    client.add_device(keyboard)

    client.bind({
        (Keycode.Yellow, Event.KeyDown): [client.switch_mode],
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
            Keycode.Up:     (mouse.start_motion, Key.up),
            Keycode.Down:   (mouse.start_motion, Key.down),
            Keycode.Left:   (mouse.start_motion, Key.left),
            Keycode.Right:  (mouse.start_motion, Key.right),
            Keycode.Ok:     (mouse.press, Button.left),
            Keycode.Play:   (mouse.press, Button.middle),
            Keycode.Pause:  (mouse.press, Button.right),
            Keycode.Back:   (keyboard.press, Key.esc),
            Keycode.Red:    (keyboard.press, Key.cmd),
            Keycode.Green:  (mouse.scroll, 0, +1),
            Keycode.Blue:   (mouse.scroll, 0, -1),
        },
        (Mode.Mouse, Event.KeyUp): {
            Keycode.Up:     (mouse.stop_motion, Key.Up),
            Keycode.Down:   (mouse.stop_motion, Key.Down),
            Keycode.Left:   (mouse.stop_motion, Key.Left),
            Keycode.Right:  (mouse.stop_motion, Key.Right),
            Keycode.Ok:     (mouse.release, Button.left),
            Keycode.Play:   (mouse.release, Button.middle),
            Keycode.Pause:  (mouse.release, Button.right),
            Keycode.Back:   (keyboard.release, Key.esc),
            Keycode.Red:    (keyboard.release, Key.cmd),
            # Keycode.Green:  (mouse.scroll, 0, +1),
            # Keycode.Blue:   (mouse.scroll, 0, -1),
        },
    })
