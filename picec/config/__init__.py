import shlex
from configparser import ConfigParser

from picec.commands import Command


class Config:

    def __init__(self):
        self.keycodes = {}
        self.bindings = {'*': {}}
        self.mode = None
        self.modes = []

    def bind(self, keybindings):
        """Set keybindings according to mode."""
        for mode, bindings in keybindings.items():
            if mode != '*':
                if self.mode is None:
                    self.mode = mode
                if mode not in self.modes:
                    self.modes.append(mode)
                    self.bindings[mode] = {}
            self.bindings[mode].update(bindings)

    def keybinding(self, mode, keycode):
        """Get command associated to keycode in current mode."""
        default = self.bindings['*'].get(keycode)
        handler = self.bindings[mode].get(keycode, default)
        return handler

    def load_file(self, filename, client):
        with open(filename) as f:
            text = f.read()
        return self.load_string(text, client)

    def load_string(self, text, client):
        """
        Load keycodes and keybindings from config file.

        Returns a new ``Config`` object that is a copy of this config merged
        with the loaded settings.

        See the ``picec/config/lgmagic.cfg`` file for example.
        """
        parser = ConfigParser()
        parser.read_string(text)

        keycodes = self.keycodes.copy()
        modes = {}

        if parser.has_section('keycode'):
            section = parser['keycode']
            for name, value in section.items():
                if not value.isnumeric():
                    raise ValueError(
                        "Invalid key code for {}: {!r}".format(name, value))
                keycodes[name] = int(value)

        for section in parser.sections():
            if section.lower().startswith('mode.'):
                mode_name = section[len('mode.'):]
                modes[mode_name] = parser.items(section)
            elif section != 'keycode':
                print("Warning: Unused section in config file:", section)

        all_modes = set(self.modes) | set(modes)
        keybindings = {mode: {} for mode in modes}

        for mode, items in modes.items():
            for key, binding in items:
                command, *args = shlex.split(binding)

                if key.isnumeric():
                    keycode = int(key)
                elif key in keycodes:
                    keycode = keycodes[key]
                else:
                    raise ValueError("Undefined key: {!r}".format(key))

                if command == 'switch' and args and args[0] not in all_modes:
                    raise ValueError("Unknown mode: {!r}".format(args[0]))

                if command in Command.commands:
                    command = Command.commands[command](client, *args)
                else:
                    raise ValueError(
                        "Invalid command: {!r} = {!r}".format(key, binding))

                keybindings[mode][keycode] = command

        config = Config()
        config.keycodes = keycodes
        config.bind(self.bindings)
        config.bind(keybindings)
        return config
