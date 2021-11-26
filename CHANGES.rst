Changes
-------

v0.0.4
~~~~~~
Date: 26.11.2021

- fix: TypeError: __init__() missing 1 required positional argument: 'app_name'
- fix: AttributeError: 'dict' object has no attribute 'setup'
- fix: AttributeError: module 'os' has no attribute 'setpgrgp'


v0.0.3
~~~~~~
Date: 25.11.2021

- spawn subprocesses in new process group
  (to avoid tearing them down with us when we are stopped)
- execute via ``bash -l`` in .service file to ensure PATH customizations are
  available. This may fix an error when autostarting the service, and will
  be useful for launching locally installed applications.
- move code to package structure
- use entrypoint for creating the executable
- rename executable from ``picec.py`` to ``picec``
- add command line option to change config
  (undocumented so far, and the API will change!)
- load config from ``~/.config/picec/config.py`` if exists
- simplify config
- bind ``matchbox-keyboard`` to red button in mouse mode
- add notification about mode changes using notify2


v0.0.2
~~~~~~
Date: 22.11.2021

- replace xdotool by ``pynput``
- make .service restart on failure


v0.0.1
~~~~~~
Date: 22.11.2021

Initial prototype:

- hard coded keybindings
- for LG TV with magic remote
- "mouse" and "keyboard" mode for controlling the mouse or cursor keys
- based on xdotool
- includes an example .service file
