def getChar():
    # figure out which function to use once, and store it in _func
    if "_func" not in getChar.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            getChar._func=msvcrt.getch

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            getChar._func=_ttyRead

    output = getChar._func()
    return output

#key[F1]        = '^[[[A' or '^[[11~'
#key[F2]        = '^[[[B' or '^[[12~'
#key[F3]        = '^[[[C' or '^[[13~'
#key[F4]        = '^[[[D' or '^[[14~'
#key[F5]        = '^[[[E' or '^[[15~'
#key[F6]        = '^[[17~'
#key[F7]        = '^[[18~'
#key[F8]        = '^[[19~'
#key[F9]        = '^[[20~'
#key[F10]       = '^[[21~'
#key[F11]       = '^[[23~'
#key[F12]       = '^[[24~'
#
#key[Shift-F1]  = '^[[25~'
#key[Shift-F2]  = '^[[26~'
#key[Shift-F3]  = '^[[28~'
#key[Shift-F4]  = '^[[29~'
#key[Shift-F5]  = '^[[31~'
#key[Shift-F6]  = '^[[32~'
#key[Shift-F7]  = '^[[33~'
#key[Shift-F8]  = '^[[34~'
#---------------- implemented the above only
#
#key[Insert]    = '^[[2~'
#key[Delete]    = '^[[3~'
#key[Home]      = '^[[1~'
#key[End]       = '^[[4~'
#key[PageUp]    = '^[[5~'
#key[PageDown]  = '^[[6~'
#key[Up]        = '^[[A'
#key[Down]      = '^[[B'
#key[Right]     = '^[[C'
#key[Left]      = '^[[D'

#key[Bksp]      = '^?'
#key[Bksp-Alt]  = '^[^?'
#key[Bksp-Ctrl] = '^H'
def getCommand():
    cmd=getChar()
    try:
        if cmd=='\x1b': # special function key, need get more
            cmd=getChar()
            if cmd=='[':
                cmd=getChar()
                if cmd=='[': # ^[[[ A-E : F1-F5
                    cmd=getChar()
                    cmd='F'+str(ord(cmd)-ord('A')+1)
                elif int(cmd)>=1 and int(cmd)<=3: # ^[[ 1-3 F6-SHIFT-F8
                    code=cmd
                    cmd=getChar()
                    getChar() # last ~
                    code=int(code+cmd)
                    if int(code)>=11 and int(code)<=15: #F1-F5
                        cmd='F'+str(code-10)
                    elif int(code)>=17 and int(code)<=21:
                        cmd='F'+str(code-11) # F6-F10
                    elif int(code)>=23 and int(code)<=24:
                        cmd='F'+str(code-12) # F11-F12
                    elif int(code)>=25 and int(code)<=26:
                        cmd='SF'+str(code-24) # SHIFT + F1-F2
                    elif int(code)>=28 and int(code)<=29:
                        cmd='SF'+str(code-25) # SHIFT + F3-F4
                    elif int(code)>=31 and int(code)<=34:
                        cmd='SF'+str(code-26) # SHIFT + F5-F8
                    else:
                        cmd=""
                else:
                    cmd=""
            else:
                cmd=""
    except (ValueError, TypeError):
        return None
    return cmd
