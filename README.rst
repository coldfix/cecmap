piCEC
=====

Simple script to control mouse cursor via CEC.

Intended for controlling raspberry pi with TV remote.


Install
~~~~~~~

You can install picec as user or root:

**as user:**

::

    pip3 install --user picec

Also, make sure to add ``~/.local/bin`` to your PATH.


**as root:**

::

    sudo pip3 install picec


Usage
~~~~~

Launch::

    picec

    # or:

    python -m picec

Enable running at startup::

    systemctl --user enable picec

Start as service::

    systemctl --user start picec
