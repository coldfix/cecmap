#! /usr/bin/env python
import cec

import argparse
import os
import subprocess
import time
from enum import Enum
from importlib import import_module
from queue import Queue, Empty


class Event(Enum):
    KeyDown = 0
    KeyUp = 1


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


def main(args=None):
    args = parse_args(args)
    os.environ.setdefault('DISPLAY', ':0')
    timestep = 0.01
    client = Client()
    print("Loading config...")
    config = import_module('picec.config.' + args.config)
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
    parser.add_argument('-c', '--config', default='lgmagic')
    return parser.parse_args(args)


class Client:

    def __init__(self, *, num_modes=2):
        self.keybindings = []
        self.num_modes = num_modes
        self.mode = 0
        self.events = Queue()
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def bind(self, rules):
        self.keybindings.extend(make_keybindings((), rules))

    def switch_mode(self, mode=None):
        if mode is None:
            mode = self.mode + 1
        else:
            mode = getattr(mode, 'value', mode)
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
