CLI colorizer
=============
This project is to colorize output of command line interface for several devices.
Goal is to ease troubleshooting and make output more pretty.

.. image:: https://realvitya.files.wordpress.com/2017/02/shint1.png

INSTALL
-------
- You will need python 2 and pexpect
- telnet and/or ssh should be installed
- I recommend installing ``virtualenv`` and install ``clicol`` into that virtual environment:
   - pip install virtualenv
   - virtualenv ~/mypython
   - source ~/mypython/bin/activate
   - pip install clicol
   - OR (after pulling git source)
   - make
   - make install
- Get clicol source:
   - git clone http://github.com/realvitya/clicol ~/clicol
   - cd ~/clicol
- Copy `clicol.cfg <https://github.com/realvitya/clicol/blob/master/doc/clicol.cfg>`_. to your $HOME directory

USAGE
-----
Run the script ``clicol-telnet`` or ``clicol-ssh`` and specify arguments as for the telnet/ssh.

clicol can be run on Windows in cygwin. If you want to use SecureCRT, you must enable sshd in cygwin and connect to localhost. It is not necessary to be administrator on the desktop for this to work. You must bind to localhost and use port number >1024.

By default clicol will colorize with all colorsets and this behaviour can be tuned in config file.
The config file can be saved in user directory and it will take preference over defaults.

Default break key is CTRL-\\

After hitting the break key you have some options:

p - pausing coloring

q - quit from session

h - print help

F1-F12 keys are shortcuts for various commands. Examples are in example config file or try help 'h' key. Shortcuts for SHIFT+F1-F8 are only working if your terminal supports this. For SecureCRT you may setup mapped keys for these to work. (for putty I don't know yet how to implement this)

*Note: If you installed into virtualenv then you must first activate it:*

**source ~/mypython/bin/activate**

Consider using aliases. A basic template can be found in *doc* folder.


Your terminal software should support ANSI colors. Putty/SecureCRT are tested. I am developing with default colorsets. If you are using other software, colors can differ somewhat.

TESTING
-------
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
