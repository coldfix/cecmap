cecmap
======

Maps CEC events to arbitrary keybindings for controlling your raspberrypi desktop via TV remote.


Install
-------

You can install *cecmap* as user or root:

**as user:**

::

    pip3 install --user cecmap

Also, make sure to add ``~/.local/bin`` to your PATH.


**as root:**

::

    sudo pip3 install cecmap

In order to see notifications when switching modes, it's also necessary to
have a notification daemon installed. I recommend ``xfce4-notifyd``::

    sudo apt install xfce4-notifyd

I also recommend installing an onscreen keyboard, e.g.::

    sudo apt install matchbox-keyboard


Usage
-----

Launch::

    cecmap

    # or:

    python -m cecmap


Running as service
------------------

Enable running at startup::

    systemctl --user enable cecmap

Start as service::

    systemctl --user start cecmap


Default keybindings
-------------------

*cecmap* comes configured with default a *Keyboard* and *Mouse* mode to get
you started (see `cecmap/config/default.cfg`_). You can freely change these
keybindings and add or override modes using the config format, see
Configuration_. The default keybindings are as follows:

.. list-table::
    :header-rows: 1

    * - Key
      - *Mouse* mode
      - *Keyboard* mode

    * - 🔵 F1 blue
      - switch mode
      - switch mode
    * - 🔴 F2 red
      - launch ``matchbox-keyboard``
      - ``<Win>``
    * - 🟢 F3 green
      - mouse wheel up
      - launch kodi
    * - 🟡 F4 yellow
      - mouse wheel down
      - launch ``chromium-browser``

    * - 🡅 up
      - move cursor up
      - ``<up>``
    * - 🡇 down
      - move cursor down
      - ``<down>``
    * - 🡄 left
      - move cursor left
      - ``<left>``
    * - 🡆 right
      - move cursor right
      - ``<right>``

    * - 🆗 select
      - left click
      - ``<enter>``
    * - ▶ play
      - middle click
      - ``<media_play_pause>``

    * - ⏸ pause
      - right click
      - ``<media_play_pause>``
    * - ⮨ exit
      - ``<esc>``
      - ``<esc>``


Configuration
-------------

*cecmap* uses a simple config format to set keycodes and keybindings. The
config to be used can be specified on the command line using the ``-c
FILE.cfg`` option. The format is as follows:

.. code-block:: cfg

    [keycode]
    KEY = <NUMBER>
    ...

    [mode.NAME]
    KEY = <command> [<args>...]
    ...

e.g.:

.. code-block:: cfg

    [keycode]
    left = 123
    yellow = 321
    ...

    [mode.Keyboard]
    left = key left
    yellow = launch kodi
    ...

For a more realistic example, see `cecmap/config/default.cfg`_.

If multiple *modes* are defined, make sure to define a keybinding that
executes the ``switch`` command. This is most easily done in the special
section ``[mode.*]`` that can be used to define fallbacks bindings that apply
globally to all modes. *cecmap* will be started in the topmost declared mode, and
cycle through modes in the order of their appearance.

Multiple config files can be passed. In this case the configuration is merged
sequentially with later files overriding earlier ones. This can be used to
e.g. load keycodes and keybindings from different files::

    cecmap \
        -c keycodes.cfg \
        -c mousemode.cfg \
        -c keymode.cfg

If no ``-c CONFIG`` option is passed on the command line, *cecmap* checks user
and system, or default configuration and uses the first that exists:

- ``$XDG_CONFIG_HOME/cecmap.cfg`` (defaulting to ``~/.config/cecmap.cfg``)
- ``/etc/cecmap.cfg``
- `cecmap/config/default.cfg`_ (distributed with the package)


.. _cecmap/config/default.cfg: https://github.com/coldfix/cecmap/blob/main/cecmap/config/default.cfg

Commands
~~~~~~~~

Currently, the following commands are supported as right hand sides of
keybindings:

.. list-table:: Commands

    * - ``launch <command> [<args>...]``
      - Start the given program. You can use shell-like quoting to pass
        arguments with spaces in them.

    * - ``toggle <command> [<args>...]``
      - Start the given program with command line options. If we have
        previously started the program, terminate it. Useful for commands such
        as ``matchbox-keyboard``.

    * - ``key <name>|<keycode>|@<letter>``
      - Type the specified key. For a list of key names, see Key_.

    * - ``button left|middle|right|<number>``
      - Perform a mouse click using the specified button. More button names
        are available, see Button_.

    * - ``scroll up|down|left|right [<ticks>]``
      - Scroll the mouse wheel in the specified direction a specified number
        of scroll ticks (default = 1).

    * - ``motion up|down|left|right``
      - Perform a mouse cursor motion along the given direction while the key
        is pressed.

    * - ``switch [<mode>]``
      - Switch to the specified ``<mode>``, or if this optional argument is
        omitted, cycle through modes in the order of their appearance in the
        config files.

.. _Key: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key
.. _Button: https://github.com/moses-palmer/pynput/blob/master/lib/pynput/mouse/_xorg.py


Keycodes
~~~~~~~~

If the default keycodes do not work as expected, you can configure the
keycodes specific to your setting. In order to determine which key corresponds
to which keycode, open a terminal and execute::

    cec-client

Watch the output as you press buttons, and write down the keycodes for the
config file.


Reloading
~~~~~~~~~

*cecmap* can be told to reload the config by sending ``SIGUSR1``, e.g.::

    pkill -USR1 cecmap

or, if started as a service::

    systemctl --user reload cecmap
