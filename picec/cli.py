import cec

import argparse
import os
import signal
import time
from importlib.resources import is_resource, read_text
from queue import Queue, Empty

from picec.config import Config
from picec.device import Keyboard, Mouse
from picec.notify import Notify


class Clock:

    def __init__(self):
        self.prev = time.perf_counter()

    def __call__(self):
        now = time.perf_counter()
        delta = now - self.prev
        self.prev = now
        return delta


def reload(client, config_file):
    """Reload config."""
    if config_file is None:
        config_home = (
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.expanduser('~/.config'))
        if os.path.exists(os.path.join(config_home, "picec.cfg")):
            config_file = os.path.join(config_home, "picec.cfg")
        elif os.path.exists('/etc/picec.cfg'):
            config_file = '/etc/picec.cfg'
        else:
            config_file = 'lgmagic'

    print("Loading config file:", config_file)
    resource = ('picec.config', config_file + '.cfg')
    if '/' not in config_file and is_resource(*resource):
        text = read_text(*resource)
    else:
        with open(config_file) as f:
            text = f.read()
    client.reset(client.config.load_string(text, client))


def main(args=None):
    args = parse_args(args)
    timestep = 0.01
    client = Client()
    signal.signal(signal.SIGUSR1, lambda *_: reload(client, args.config))
    reload(client, args.config)

    print("Initializing...")
    client.connect()
    print("Ready")
    clock = Clock()
    while True:
        timeout = timestep if any(d.active for d in client.devices) else None
        events = client.recv(timeout)
        time_delta = clock()
        for device in client.devices:
            if device.active:
                device.dispatch(time_delta)
        for event in events:
            client.dispatch(*event)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=None)
    return parser.parse_args(args)


class Client:

    def __init__(self):
        self.config = Config()
        self.mode = None
        self.events = Queue()
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self.devices = [self.mouse, self.keyboard]
        self.notify = Notify("picec", timeout=3000)

    def reset(self, config):
        self.config = config
        if self.mode not in config.modes:
            self.mode = config.mode

    def switch(self, mode=None):
        """Switch to the given or the next mode."""
        if mode is None:
            current = self.config.modes.index(self.mode)
            mode = self.config.modes[(current + 1) % len(self.config.modes)]
        if self.mode != mode:
            self.mode = mode
            self.notify("Mode: {}".format(mode))

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
        handler = self.config.keybinding(self.mode, keycode)
        if handler:
            handler(duration)


if __name__ == '__main__':
    main()
