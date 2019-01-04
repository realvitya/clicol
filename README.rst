=============
CLI colorizer
=============

This project is to colorize output of command line interface for devices where CLI is not colored by default.
Goal is to ease troubleshooting and make output more pretty.

.. image:: http://img.shields.io/badge/license-GPLv3-blue.svg
   :target: https://www.gnu.org/copyleft/gpl.html
   :alt: License

.. image:: https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg
   :target: https://developer.cisco.com/codeexchange/github/repo/realvitya/clicol
   :alt: Cisco Devnet Published

.. image:: https://realvitya.files.wordpress.com/2017/02/shint1.png

INSTALL
=======
- You will need python 2 and pexpect
- telnet and/or ssh should be installed
- I recommend installing virtualenv_ and install clicol_ into that virtual environment:
   - pip install virtualenv
   - virtualenv ~/mypython
   - source ~/mypython/bin/activate
   - pip install clicol
   - OR (after pulling git source)
     - pip install clicol-xxxx.zip
- Get clicol source:
   - git clone https://github.com/realvitya/clicol ~/clicol
   - cd ~/clicol
- Copy `clicol.cfg <https://github.com/realvitya/clicol/blob/master/doc/clicol.cfg>`_. to your $HOME directory

USAGE
=====
Run the script ``clicol-telnet`` or ``clicol-ssh`` and specify arguments as for the telnet/ssh.

clicol can be run on Windows in cygwin_. If you want to use SecureCRT_, you must enable sshd in cygwin_ and connect to localhost. It is not necessary to be administrator on the desktop for this to work. You must bind to localhost and use port number >1024.

By default clicol will colorize with all colorsets and this behaviour can be tuned in config file.
The config file can be saved in user directory and it will take preference over defaults.

Default break key is CTRL-\\

After hitting the break key you have some options:

p - pausing coloring

q - quit from session

h - print help

T - highlight regex (set regex in runtime to highligh something important)

F1-F12 keys are shortcuts for various commands. Examples are in example config file or try help 'h' key. Shortcuts for SHIFT+F1-F8 are only working if your terminal supports this. For SecureCRT_ you may setup mapped keys for these to work. (for Putty_ I don't know yet how to implement this)

*Note: If you installed into virtualenv then you must first activate it:*

**source ~/mypython/bin/activate**

Consider using aliases. A basic template can be found in *doc* folder.


Your terminal software should support ANSI colors. Putty_/SecureCRT_ are tested. I am developing with default colorsets. If you are using other software, colors can differ somewhat.

TESTING
=======
You can list all supported matchers and see them in action. This is good to create a list of matcher and filter on those only. This way one can select the preferred matchers if finds all of them disturbing.
Run the script ``clicol-test {regex}``

Use case examples:

List all matcher:

``clicol-test ".*"``

List only BGP matchers:

``clicol-test ".*bgp.*"``

List only certain matchers:

``clicol-test ".*ipv4|cisco_if_stats|juniper_if"``

Then the desired regex can be specified in the clicol.cfg in your $HOME and only these matchers will be used.

Output can be tested by running ``clicol-file {filename}`` script. This will colorize the textfile and dump it. Good for testing.

CUSTOMIZING
===========
You can override or extend the colors and regexes so you can modify default behaviour and view.
This can be done by creating the customized files in the format below. You may find examples in default ini files here

``ls -l $VIRTUAL_ENV/lib/python2*/site-packages/clicol/ini``

Custom colors
-------------
``$HOME/clicol_customcolors.ini``

This file is for overriding extending current colorset.
Example:
::

        [colors]
        c_blue     :\033[94m

Custom colortable
-----------------
``$HOME/clicol_customct.ini``

This file is for overriding or extending keywords for colors.
Example:
::

        [colortable]
        #add blinking to high alert color:
        highalert              = %(c_blink)s%(c_u_lred)s
 
Custom colormap
---------------
``$HOME/clicol_customcmap.ini``

This file is for overriding or extending rules for recoloring/matching.
Example:
::

        #disable ipv6 coloring
        [common_ipv6]
        disabled=1
        
        #alter coloring for 'shutdown'
        [common_shut]
        #replacement=%(alert)s\1%(default)s
        replacement=%(lowalert)s\1%(default)s

You can test your changes: ``clicol-test common_shut``

License and Copyright
=====================

clicol_ is licensed GPLv3_; Copyright `Viktor Kertesz`, 
2017-2018.

Author
======

clicol_ was written by Viktor Kertesz (vkertesz2 [~at~] gmail [/dot\] com).

.. _clicol: https://pypi.org/project/clicol
.. _`GPLv3`: http://www.gnu.org/licenses/gpl-3.0.html
.. _SecureCRT: https://www.vandyke.com/products/securecrt
.. _cygwin: https://www.cygwin.com
.. _virtualenv: https://pypi.org/project/virtualenv
.. _Putty: https://www.chiark.greenend.org.uk/~sgtatham/putty/
