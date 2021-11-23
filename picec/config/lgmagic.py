"""
2-mode configuration for LG with MagicRemote.
"""

from picec import launch
from picec.device import Key, Button, Keyboard, Mouse


class Mode:
    Mouse = 0
    Keyboard = 1


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


def setup(client):
    mouse = Mouse()
    keyboard = Keyboard()

    client.set_mode(Mode.Mouse)
    client.add_device(mouse)
    client.add_device(keyboard)

    client.bind({
        Mode.Keyboard: {
            Keycode.Up:     (keyboard.key, Key.up),
            Keycode.Down:   (keyboard.key, Key.down),
            Keycode.Left:   (keyboard.key, Key.left),
            Keycode.Right:  (keyboard.key, Key.right),
            Keycode.Ok:     (keyboard.key, Key.enter),
            Keycode.Play:   (keyboard.key, Key.media_play_pause),
            Keycode.Pause:  (keyboard.key, Key.media_play_pause),
            Keycode.Back:   (keyboard.key, Key.esc),
            Keycode.Red:    (keyboard.key, Key.cmd),
            Keycode.Green:  (launch, "kodi"),
            Keycode.Blue:   (launch, "chromium-browser"),
            Keycode.Yellow: (client.set_mode, Mode.Mouse),
        },
        Mode.Mouse: {
            Keycode.Up:     (mouse.motion, Key.up),
            Keycode.Down:   (mouse.motion, Key.down),
            Keycode.Left:   (mouse.motion, Key.left),
            Keycode.Right:  (mouse.motion, Key.right),
            Keycode.Ok:     (mouse.button, Button.left),
            Keycode.Play:   (mouse.button, Button.middle),
            Keycode.Pause:  (mouse.button, Button.right),
            Keycode.Back:   (keyboard.key, Key.esc),
            Keycode.Red:    (keyboard.key, Key.cmd),
            Keycode.Green:  (mouse.scroll, 0, +1),
            Keycode.Blue:   (mouse.scroll, 0, -1),
            Keycode.Yellow: (client.set_mode, Mode.Keyboard),
        },
    })
