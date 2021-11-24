#! /usr/bin/env python
import cec

import argparse
import importlib
import os
import runpy
import subprocess
import time
from queue import Queue, Empty


def launch(*args, **kwargs):
    return subprocess.Popen(args, preexec_fn=os.setpgrgp, **kwargs)


class StartStop:

    def __init__(self, *argv):
        self.argv = argv
        self.proc = None

    def __call__(self):
        if self.proc is None:
            self.proc = launch(*self.argv)
        else:
            self.proc.terminate()
            self.proc = None


def make_handler(handler):
    func, *args = handler
    if isinstance(func, (list, tuple)):
        return handler
    else:
        return ((func, None), *args)


class Clock:

    def __init__(self):
        self.prev = time.perf_counter()

    def __call__(self):
        now = time.perf_counter()
        delta = now - self.prev
        self.prev = now
        return delta


def main(args=None):
    args = parse_args(args)
    os.environ.setdefault('DISPLAY', ':0')
    timestep = 0.01
    client = Client()
    print("Loading config...")

    config_file = args.config
    if config_file is None:
        config_home = (
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.expanduser('~/.config'))
        if os.path.exists(os.path.join(config_home, "picec/config.py")):
            config_file = os.path.join(config_home, "picec/config.py")
        else:
            config_file = "lgmagic"

    if os.path.isfile(config_file):
        config = runpy.run_path(config_file)
    elif importlib.util.find_spec('picec.config.' + config_file):
        config = runpy.run_module('picec.config.' + config_file)
    else:
        config = runpy.run_module(config_file)

    config.setup(client)
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
        self.keybindings = {}
        self.mode = 0
        self.events = Queue()
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def bind(self, rules):
        for mode, bindings in rules.items():
            self.keybindings.setdefault(mode, {}).update({
                key: make_handler(handler)
                for key, handler in bindings.items()
            })

    def set_mode(self, mode):
        self.mode = mode

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
        default = self.keybindings.get(any, {}).get(keycode)
        handler = self.keybindings.get(self.mode, {}).get(keycode, default)
        if handler:
            funcs, *args = handler
            func = funcs[duration > 0]
            if func:
                func(*args)


if __name__ == '__main__':
    main()
