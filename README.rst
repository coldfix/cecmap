piCEC
=====

Simple script to control mouse cursor via CEC.

Intended for controlling raspberry pi with TV remote.


Install
~~~~~~~

In addition to the picec python script, you will also need xdotool::

    sudo apt install xdotool


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

    picec.py

Enable running at startup::

    systemctl --user enable picec

Start as service::

    systemctl --user start picec
