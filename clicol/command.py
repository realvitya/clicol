from __future__ import print_function
from __future__ import unicode_literals
from builtins import input
import re
import sys
try:
    import readline
except ImportError:
    pass

PY3 = sys.version_info.major == 3


def getchar():
    """
    Read a single character from terminal
    :return: read character as unicode string
    """
    # figure out which function to use once, and store it in _func
    if "_func" not in getchar.__dict__:
        try:
            # for Windows-based systems
            import msvcrt  # If successful, we are on Windows
            getchar._func = msvcrt.getch
        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty
            import termios  # raises ImportError if unsupported

            def _ttyread():
                fd = sys.stdin.fileno()
                oldsettings = termios.tcgetattr(fd)

                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldsettings)

                return answer

            getchar._func = _ttyread

    output = getchar._func()
    return output

# Key codes:
# key[F1]        = '^[[[A' or '^[[11~'
# key[F2]        = '^[[[B' or '^[[12~'
# key[F3]        = '^[[[C' or '^[[13~'
# key[F4]        = '^[[[D' or '^[[14~'
# key[F5]        = '^[[[E' or '^[[15~'
# key[F6]        = '^[[17~'
# key[F7]        = '^[[18~'
# key[F8]        = '^[[19~'
# key[F9]        = '^[[20~'
# key[F10]       = '^[[21~'
# key[F11]       = '^[[23~'
# key[F12]       = '^[[24~'
#
# key[Shift-F1]  = '^[[25~'
# key[Shift-F2]  = '^[[26~'
# key[Shift-F3]  = '^[[28~'
# key[Shift-F4]  = '^[[29~'
# key[Shift-F5]  = '^[[31~'
# key[Shift-F6]  = '^[[32~'
# key[Shift-F7]  = '^[[33~'
# key[Shift-F8]  = '^[[34~'
# ---------------- implemented the above only
#
# key[Insert]    = '^[[2~'
# key[Delete]    = '^[[3~'
# key[Home]      = '^[[1~'
# key[End]       = '^[[4~'
# key[PageUp]    = '^[[5~'
# key[PageDown]  = '^[[6~'
# key[Up]        = '^[[A'
# key[Down]      = '^[[B'
# key[Right]     = '^[[C'
# key[Left]      = '^[[D'

# key[Bksp]      = '^?'
# key[Bksp-Alt]  = '^[^?'
# key[Bksp-Ctrl] = '^H'


def getcommand():
    """
    Returns key command read in the following formats:
        F1 for hitting first function key
        F2
        ..
        F12
        SF1..SF8 for SHIFT + function key
    :return: hit command key in string format
    """
    cmd = getchar()
    try:
        if cmd == '\x1b':  # special function key, need get more
            cmd = getchar()
            if cmd == '[':
                cmd = getchar()
                if cmd == '[':  # ^[[[ A-E : F1-F5
                    cmd = getchar()
                    cmd = 'F' + str(ord(cmd) - ord('A') + 1)
                elif 1 <= int(cmd) <= 3:  # ^[[ 1-3 F6-SHIFT-F8
                    code = cmd
                    cmd = getchar()
                    getchar()  # last ~
                    code = int(code + cmd)
                    if 11 <= int(code) <= 15:  # F1-F5
                        cmd = 'F' + str(code - 10)
                    elif 17 <= int(code) <= 21:
                        cmd = 'F' + str(code - 11)  # F6-F10
                    elif 23 <= int(code) <= 24:
                        cmd = 'F' + str(code - 12)  # F11-F12
                    elif 25 <= int(code) <= 26:
                        cmd = 'SF' + str(code - 24)  # SHIFT + F1-F2
                    elif 28 <= int(code) <= 29:
                        cmd = 'SF' + str(code - 25)  # SHIFT + F3-F4
                    elif 31 <= int(code) <= 34:
                        cmd = 'SF' + str(code - 26)  # SHIFT + F5-F8
                    else:
                        cmd = ""
                else:
                    cmd = ""
            else:
                cmd = ""
    except (ValueError, TypeError):
        return None
    return cmd


def getregex():
    regexstr = input("\r" + " " * 100 + "\rHighlight regex: ")
    if not PY3:
        regexstr = regexstr.decode('utf-8')
    try:
        output = re.compile('(' + regexstr + ')')
    except re.error:
        print("Wrong regex!")
        return ""
    if regexstr == "":
        return ""
    return output


# Source: http://stackoverflow.com/a/566752/2646228


def getterminalsize():
    """
    Get terminal size in rows and columns
    Source: http://stackoverflow.com/a/566752/2646228
    :return: if feature is supported, a tuple of (lines,columns)
    """
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                 '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[0]), int(cr[1])
