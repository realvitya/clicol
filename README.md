CLI colorizer
=============

This project is to colorize output of command line interface for devices where CLI is not colored by default. Goal is to ease troubleshooting and make output more pretty.

[![License](http://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/copyleft/gpl.html)
[![Cisco Devnet Published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/realvitya/clicol)

![image](https://realvitya.files.wordpress.com/2017/02/shint1.png)

INSTALL
-------

 -   You will need python 2.6+/3 and pexpect
 -   telnet and/or ssh should be installed
 -   I recommend installing [virtualenv](https://pypi.org/project/virtualenv) and install [clicol](https://pypi.org/project/clicol) into that virtual environment:
        *   `pip install virtualenv`
        *   `virtualenv ~/mypython`
        *   `source ~/mypython/bin/activate`
        *   `pip install clicol`
        *   OR (after pulling git source)
            *   `pip install clicol-xxxx.zip`

 -   To get clicol source:
        *   `git clone https://github.com/realvitya/clicol ~/clicol`
        *   `cd ~/clicol`

 -   Copy
    [clicol.cfg](https://github.com/realvitya/clicol/blob/master/doc/clicol.cfg) to your $HOME directory and modify to your needs

USAGE
-----

Run the script `clicol-telnet` or `clicol-ssh` and specify arguments as for the telnet/ssh.<BR>
Run the script `clicol-cmd` and any command with arguments to pimp up any non-colored cli command.

Available command line option for clicol:<BR>
`clicol-{telnet|ssh} [--c {colormap}] [--cfgdir {dir}] [--caption {caption}] [args]`<BR>
`clicol-file         [--c {colormap}] [--cfgdir {dir}] {inputfile}`<BR>
`clicol-cmd          [--c {colormap}] [--cfgdir {dir}] {command} [args]`<BR>
`clicol-test         [--c {colormap}] [--cfgdir {dir}] {colormap regex name (e.g.: '.*' or 'cisco_if|juniper_if')}`

Explanation for arguments:<BR>
`--c {colormap}` : use only specified colormap (`all`, `common`, `cisco`, `juniper`) Defaulted to `all`<BR>
`--cfgdir {dir}` : use specified config directory. Defaulted to `~/.clicol`<BR>
`--caption {caption}`: use this caption template (you can use `%(host)s` for connected device and `%(hostname)s` for actual host name) Defaulted to `%(host)s`

clicol can be run on Windows in [cygwin](https://www.cygwin.com). If you want to use [SecureCRT](https://www.vandyke.com/products/securecrt), you must enable sshd in [cygwin](https://www.cygwin.com) and connect to localhost. It is not necessary to be administrator on the desktop for this to work. You must bind to localhost and use port number >1024.

By default clicol will colorize with all colorsets and this behaviour can be tuned in config file. The config file can be saved in user directory and it will take preference over defaults.

Default break key is CTRL-\

After hitting the break key you have some options:<BR>
p - pausing coloring<BR>
q - quit from session<BR>
h - print help<BR>
T - highlight regex (set regex in runtime to highligh something important)

F1-F12 keys are shortcuts for various commands. Examples are in example config file or try help 'h' key. Shortcuts for SHIFT+F1-F8 are only working if your terminal supports this. For [SecureCRT](https://www.vandyke.com/products/securecrt) you may setup mapped keys for these to work. (for [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/) I don't know yet how to implement this)

*Note: If you installed into virtualenv then you must first activate it:*

**source ~/mypython/bin/activate**

Consider using aliases. A basic template can be found in *doc* folder.

Your terminal software should support ANSI colors. [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/)/[SecureCRT](https://www.vandyke.com/products/securecrt) are tested. I am developing with default colorsets. If you are using other software, colors can differ somewhat.

TESTING
-------

You can list all supported matchers and see them in action. This is good to create a list of matcher and filter on those only. This way one can select the preferred matchers if finds all of them disturbing. Run the script `clicol-test {regex}`

Use case examples:

List all matcher:

`clicol-test ".*"`

List only BGP matchers:

`clicol-test ".*bgp.*"`

List only certain matchers:

`clicol-test ".*ipv4|cisco_if_stats|juniper_if"`

Then the desired regex can be specified in the clicol.cfg in your $HOME and only these matchers will be used.

Output can be tested by running `clicol-file {filename}` script. This will colorize the textfile and dump it. Good for testing.

CUSTOMIZING
-----------

You can override or extend the colors and regexes so you can modify default behaviour and view. This can be done by creating the customized files in the format below. You may find examples in default ini files here

`ls -l $VIRTUAL_ENV/lib/python2*/site-packages/clicol/ini`

Default configuration directory is `$HOME/.clicol`. All configuration or plugin file should be in that directory! Configuration files in the user directory will override the .clicol directory files!

### Custom colors

`clicol_customcolors.ini`

This file is for overriding extending current colorset. Example:

    [colors]
    c_blue     :\033[94m

### Custom colortable

`clicol_customct.ini`

This file is for overriding or extending keywords for colors. Example:

    [colortable]
    #add blinking to high alert color:
    highalert              = %(c_blink)s%(c_u_lred)s

### Custom colormap

`clicol_customcmap.ini`

This file is for overriding or extending rules for recoloring/matching.
Example:

    #disable ipv6 coloring
    [common_ipv6]
    disabled=1

    #alter coloring for 'shutdown'
    [common_shut]
    #replacement=%(alert)s\1%(default)s
    replacement=%(lowalert)s\1%(default)s

You can test your changes: `clicol-test common_shut`

PLUGINS
-------

It is possible to extend CLICOL's capabilities with plugins. The main idea is that plugins can have external dependencies and can do external calls to manipulate output. Currently two functions are called from CLICOL to a plugin: `preprocess` and `postprocess`. These are to be called before CLICOL colorization and after so a plugin can have a chance to see the text and manipulate it at these points.

For example implementation you may check the builtin plugin in the `builtinplugins` folder or external projects like the followings: 
1. [AS path resolver](https://github.com/realvitya/clicol_plugin_aspath)
2. [Extra plugins](https://github.com/realvitya/clicol_plugin_extra)

### Installing plugin

After installing the plugin with pip, it must be activated in `$HOME/.clicol/plugins.cfg` configuration file. If that file did not exist or the section does not exist for the plugin, it won't be loaded.

Section name must be the plugin name in lower case!

Example `plugins.cfg`:
      
      [humannumbers]
      # Disable HumanNumbers by default:
      active=no

CLICOL reserved attribute is `active`. Any other can be used by the plugins. If `active` is not present or has positive value, then the plugin will be loaded. If the section is _not_ existing for a given plugin, it is considered as disabled.

### Develop plugins

There is a documentation about how to develop plugins for CLICOL at [wiki page](https://github.com/realvitya/clicol/wiki/Plugin-development)

License and Copyright
---------------------

[clicol](https://pypi.org/project/clicol) is licensed [GPLv3](http://www.gnu.org/licenses/gpl-3.0.html) Copyright Viktor Kertesz, 2017-2020

Author
------

[clicol](https://pypi.org/project/clicol) was written by Viktor Kertesz
(vkertesz2 [~at~] gmail [/dot] com).
