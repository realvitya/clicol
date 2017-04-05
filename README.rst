CLI colorizer
=============
This project is to colorize output of command line interface for several devices.
Goal is to ease troubleshooting and make output more pretty.

.. image:: https://realvitya.files.wordpress.com/2017/02/shint1.png

INSTALL
-------
- You will need python 2 and pexpect
- telnet and/or ssh should be installed
- Get clicol:
   - git clone http://github.com/realvitya/clicol ~/clicol
   - cd ~/clicol
- I recommend installing ``virtualenv`` and install ``clicol`` into that virtual environment:
   - pip install virtualenv
   - virtualenv ~/mypython
   - source ~/mypython/bin/activate
   - pip install clicol (latest stable)
   - OR (after pulling git source)
   - make
   - make install
- Copy clicol.cfg to your $HOME directory

USAGE
-----
Run the script ``clicol-telnet`` or ``clicol-ssh`` and specify arguments a
s for the telnet/ssh.

*Note: If you installed into virtualenv then you must first activate it:*

**source ~/mypython/bin/activate**

Consider using aliases. A basic template can be found in *example* folder.


Your terminal software should support ANSI colors. Putty/SecureCRT are tested. I am developing with default Putty ANSI colorset. If you are using other software, colors can differ somewhat.
