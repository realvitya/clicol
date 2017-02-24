CLI colorizer
=============
This project is to colorize output of command line interface for several devices.
Goal is to ease trouble shooting and make output more pretty.

INSTALL
-------
- You will need python 2 and pexpect
- telnet and/or ssh should be installed
- Get clicol:
  - git clone http://github.com/realvitya/clicol ~/clicol
  - cd ~/clicol
- I recommend installing virtualenv and install clicol into that virtual environment:
  - pip install virtualenv
  - virtualenv ~/mypython
  - source ~/mypython/bin/activate
  - make
  - make install
- Copy clicol.cfg to your $HOME directory

USAGE
-----
Run the script clicol-telnet or clicol-ssh and specify arguments as for the telnet/ssh.
Your terminal software should support ANSI colors. Putty/SecureCRT are tested. I am developing with default Putty ANSI colorset. If you are using other software, colors can differ somewhat.
