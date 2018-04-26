#!/usr/bin/python

import os
import sys
import re
import string
import pexpect
import ConfigParser
import timeit
import threading
import time
from pkg_resources import resource_filename
from importlib import import_module
from command import getCommand
from __init__ import __version__

#Global variables
conn = ''        # connection handler
buffer = ''      # input buffer
lastline = ''    # input buffer's last line
is_break = False # is break key pressed?
effects = set()  # state effects set
ct = dict()      # color table (contains colors)
cmap = list()    # color map (contains coloring rules)
pause = 0        # if true, then coloring is paused
# match for interactive input (prompt,eof)
debug = 0        # global debug (D: hidden command)
timeout = 0      # counts timeout
maxtimeout = 0   # maximum timeout (0 turns off this feature)
prevents = 0     # counts timeout prevention
maxprevents = 0  # maximum number of timeout prevention (0 turns this off)
RUNNING = True   # signal to timeoutcheck
bufferlock = threading.Lock()
#Interactive regex matches for
# - prompt (asd# ) (all)
# - question ([yes]) (cisco)
# - more (-more-) (cisco,juniper)
# - restore coloring (\x1b[m) (linux)
# possible chars: "\):>#$/- "
INTERACT=re.compile(r"(?i)^(" # START of whole line matches
                    "[^* ]+([\]\>\#\$][: ]?)(.*)" # prompt
                    "| ?<?-+ ?\(?more(?: [0-9]{1,2}%)?\)? ?-+>? ?([\b ]+)?" # more (\b can be at the end when excessive enters are pressed
                    "|\x1b\[m"                   # color escape sequence
                    "|username: ?"
                    "|password: ?"
                    ")$"                         # END of whole line match
                    "|\]:? ?$" # probably question (reload? [yes])
                    ,flags=re.S)

def timeoutcheck(maxwait=1.0):
    global bufferlock, debug, timeout, maxtimeout, buffer
    global RUNNING

    timeout = time.time()
    while RUNNING:
        time.sleep(0.33) # time clicks we run checks
        now=time.time()
        # Check if there was user input in the specified time range
        if maxtimeout>0 and (now-timeout)>=maxtimeout:
            preventtimeout()       # send something to prevent timeout on device
            timeout=time.time()    # reset timeout
        # Check if there is some output stuck at buffer we should print out
        # (to mitigate unresponsibleness)
        bufferlock.acquire()
        if (now-timeout)>maxwait and len(buffer)>0: #send out buffer
            if debug>=1: print "\r\n\033[38;5;208mTOB-",repr(buffer),"\033[0m\r\n" # DEBUG
            sys.stdout.write(colorize(buffer))
            sys.stdout.flush()
            buffer=""
            timeout=time.time()
        bufferlock.release()

def preventtimeout():
    global conn, prevents, maxprevents

    prevents+=1
    if maxprevents<=0 or prevents<=maxprevents:
        conn.send("\x0C")

def printhelp(shortcuts):
    print "q: quit program"
    print "p: pause coloring"
    print
    print "Shortcuts"
    for (key,value) in shortcuts:
        print "%s: \"%s\"" % (key.upper(),value.strip(r'"'))

def colorize(text,only_effect=[]):
    #text       : input string to colorize
    #only_effect: select specific regex group(with specified effect) to work with
    global effects, cmap, conn, timeoutact, debug
    colortext=""
    if debug>=2: start=timeit.default_timer()
    for line in text.splitlines(True): 
        cmap_counter=0
        if debug>=2: print "\r\n\033[38;5;208mC-",repr(line),"\033[0m\r\n" # DEBUG
        if debug>=3: print "\r\n\033[38;5;208mCCM-",repr(cmap),"\033[0m\r\n" # DEBUG
        for i in cmap:
            cmap_counter+=1
            matcher=False
            #try: 
            matcher=i[0] # is matcher?
            prio   =i[1]   # priority
            effect =i[2]   # invokes other rules
            dep    =i[3]   # dependency on effect
            reg    =i[4]   # regexp match string
            rep    =i[5]   # replacement string
            option =i[6]   # match options (continue,break,clear)
            cdebug =i[7] # debug
            name   =i[8] # regex name
            #except IndexError:
                #if len(i) == 5:
                #    #this is a matcher
                #    matcher=True
                #elif len(i) == 7:
                #    #don't have debug
                #    cdebug=False
                #else:
                    #raise
            if only_effect!=[] and effect not in only_effect: # check if only specified regexes should be used
                continue # move on to the next regex
            if len(dep)>0 and dep not in effects: # we don't meet our dependency
                continue # move on to the next regex
            if matcher:
                if reg.search(line):
                    effects.add(effect)
                if 'timeoutwarn' in effects and timeoutact:
                    #conn.send("\x05") # CTRL-E (goto end of line)
                    #conn.send("\x0C") # CTRL-L (display again)
                    preventtimeout()
                continue

            origline=line
            if option == 2: #need to cleanup existing coloring (CLEAR)
                backupline=line
                origline=re.sub('\x1b[^m]*m','',line)
                if debug>=3: print "\r\n\033[38;5;208mCCL-",origline,"\033[0m\r\n" # debug
            line=reg.sub(rep,origline)
            if cdebug:
                print "\r\n\033[38;5;208mD-",repr(origline), repr(line), repr(effects), "\033[0m\r\n" # debug
            if line != origline: # we have a match
                if debug>=2: print "\r\n\033[38;5;208mCM-",name,"\033[0m\r\n" # debug
                if len(effect)>0: # we have an effect
                    effects.add(effect)
                if 'prompt' in effects: # prompt eliminates all effects
                    effects=set()
                if option > 0:
                    break
            elif option == 2: # need to restore existing coloring as there was no match (by CLEAR)
                line=backupline
        if debug>=2: print "\033[38;5;208mCC-%d\033[0m" % cmap_counter         
        colortext+=line
    if debug>=2: print "\r\n\033[38;5;208mCT-%f\033[0m\r\n" % (timeit.default_timer()-start)
    return colortext

def ifilter(input):
    global is_break, timeout, prevents

    is_break = input=='\x1c'
    if not is_break: timeout=time.time(); prevents=0
    return input

def ofilter(input):
    global buffer
    global pause # coloring must be paused
    global lastline
    global debug
    global bufferlock

    # Coloring is paused by escape character
    if pause:
        return input

    bufferlock.acquire() # we got input, have to access buffer exclusively
    try:
        # If not ending with linefeed we are interacting or buffering
        if not (input[-1]=="\r" or input[-1]=="\n"):
            #collect the input into buffer
            buffer += input
            if debug: print "\r\n\033[38;5;208mI-",repr(input),"\033[0m\r\n" # DEBUG
            lastline=buffer.splitlines(True)[-1]
            if debug: print "\r\n\033[38;5;208mL-",repr(lastline),"\033[0m\r\n" # DEBUG
            if debug: print "\r\n\033[38;5;208mB-",repr(buffer),"\033[0m\r\n" # DEBUG
            #special characters. e.g. moving cursor
            #if input not starts with \b then it's sg like more or anything device wants to hide.
            #regular text can follow which we want to colorize
            if ("\a" in lastline or "\b" in lastline) and (lastline[0]!="\a" and lastline[0]!="\b") and input==lastline:
                bufout=buffer
                buffer=""
                return colorize(bufout,["prompt"])
            if INTERACT.search(lastline): # prompt or question at the end
                bufout=buffer
                buffer = ""
                return colorize(bufout)

            if len(buffer)<100:  # interactive or end of large chunk
                bufout=buffer
                if "\r" in input or "\n" in input: # multiline input, not interactive
                    bufout="".join(buffer.splitlines(True)[:-1]) # all buffer except last line
                    buffer=lastline # delete printed text. last line remains in buffer
                    return colorize(bufout)
                elif buffer==input: # interactive
                    buffer = ""
                    return colorize(bufout,["prompt","ping"]) # colorize only short stuff (up key,ping)
                else:             # need to collect more output
                    return ""
            else: # large data. we need to print until last line which goes into buffer
                bufout="".join(buffer.splitlines(True)[:-1]) # all buffer except last line
                if bufout == "": # only one line was in buffer
                    return ""
                else:
                    buffer=lastline # delete printed text. last line remains in buffer
                    return colorize(bufout)
        else:
            if debug: print "\r\n\033[38;5;208mNI-",repr(input),"\033[0m\r\n" # DEBUG
            #Got linefeed, dump buffer
            bufout = buffer+input
            buffer = ""
            return colorize(bufout)
    finally:
        bufferlock.release()

def merge_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def main():
    global conn, ct, cmap, pause, timeoutact, terminal, buffer, lastline, debug
    global is_break
    global maxtimeout, maxprevents
    global RUNNING

    default_config={'colortable' :r'dbg_net',
                    'terminal'   :r'securecrt',
                    'regex'      :r'all',
                    'timeoutact' :r'true',
                    'debug'      :r'0',
                    'maxtimeout' :r'0',
                    'maxprevents':r'0',
                    'maxwait'    :r'1.0',
                    'F1'         :r'show ip interface brief | e unassign\r',
                    'F2'         :r'show ip bgp sum\r',
                    'F3'         :r'show ip bgp vpnv4 all sum\r',
                    'F4'         :r'"ping "', # space requires quoting
                    'F5'         :r'',
                    'F6'         :r'',
                    'F7'         :r'',
                    'F8'         :r'',
                    'F9'         :r'',
                    'F10'        :r'',
                    'F11'        :r'',
                    'F12'        :r'',
                    'SF1'        :r'show interface terse | match inet\r',
                    'SF2'        :r'show bgp summary\r',
                    'SF3'        :r'',
                    'SF4'        :r'',
                    'SF5'        :r'',
                    'SF6'        :r'',
                    'SF7'        :r'',
                    'SF8'        :r'',}
    try:
        config = ConfigParser.SafeConfigParser(default_config,allow_no_value=True)
    except TypeError:
        config = ConfigParser.SafeConfigParser(default_config) # keep compatibility with pre2.7
    starttime = time.time()
    config.add_section('clicol')
    config.read(['/etc/clicol.cfg', 'clicol.cfg', os.path.expanduser('~/clicol.cfg')])
    terminal = config.get('clicol','terminal')
    shortcuts=filter(lambda (o,v): re.match(r'[sS]?[fF][0-9][0-9]?',o) and v, config.items('clicol')) # read existing shortcuts
    shortcuts.sort(key=lambda (o,v): o) # sort by function key
    cct = config.get('clicol','colortable')
    timeoutact = config.getboolean('clicol','timeoutact')
    maxtimeout = config.getint('clicol','maxtimeout')
    maxprevents= config.getint('clicol','maxprevents')
    debug = config.getint('clicol','debug')
    
    colors=ConfigParser.SafeConfigParser()
    colors.add_section('colors')
    colors.read([resource_filename(__name__,'ini/colors_'+terminal+'.ini'),os.path.expanduser('~/clicol_customcolors.ini')])

    ctfile = ConfigParser.SafeConfigParser(dict(colors.items('colors')))
    del colors
    ctfile.add_section('colortable')
    if cct == "dbg_net" or cct == "lgb_net":
        ctfile.read([resource_filename(__name__,'ini/ct_'+cct+'.ini'),os.path.expanduser('~/clicol_customct.ini')])
    else:
        print "No such colortable: "+cct
        exit(1)

    default_cmap={
             'matcher'     : '0',
             'priority'    : '100',
             'effect'      : '',
             'dependency'  : '',
             'regex'       : '',
             'replacement' : '',
             'options'     : '1', #CONTINUE=0,BREAK=1,CLEAR=2 as below
             'debug'       : '0',
             'disabled'    : '0',
             'BOL'         : '(^(?: ?<?-+ ?\(?[mM][oO][rR][eE](?: [0-9]{1,2}%%)?\)? ?-+>? ?)?(?:[\b ]+)|^)',
             'BOS'         : string.replace("(?:"+dict(ctfile.items('colortable'))['default']+r'|\b)',r'[','\['),
             'CONTINUE'    : '0',
             'BREAK'       : '1',
             'CLEAR'       : '2',
             }
    cmaps=ConfigParser.SafeConfigParser(merge_dicts(dict(ctfile.items('colortable')),default_cmap))
    del ctfile
    regex = config.get('clicol','regex')
    if regex == "all":
        regex = '.*'
    try:
        if len(sys.argv)>1 and sys.argv[1] == '--c': # called with specified colormap regex
            regex = sys.argv[2]
            del sys.argv[1] # remove --c from args
            del sys.argv[1] # remove colormap regex string from args
    except: # index error, wrong call
        cmd = 'error'
    for cm in ["common","cisco","juniper"]:
        cmaps.read(resource_filename(__name__,'ini/cm_'+cm+'.ini'))
    cmaps.read([os.path.expanduser('~/clicol_customcmap.ini')])
    for cmap_i in cmaps.sections():
        c=dict(cmaps.items(cmap_i))
        if re.match(regex,cmap_i): # configured rules only
            if debug>=3: print repr([c['matcher'],c['priority'],c['effect'],c['dependency'],c['regex'],c['replacement'],c['options'],c['debug']])
            if bool(int(c['disabled'])<1):
                cmap.append([bool(int(c['matcher'])>0),int(c['priority']),c['effect'],c['dependency'],re.compile(c['regex']),c['replacement'],int(c['options']),int(c['debug']),cmap_i])
    cmap.sort(key=lambda match: match[1]) # sort colormap based on priority

    #Check how we were called
    # valid options: clicol-telnet, clicol-ssh, clicol-test
    cmd = str(os.path.basename(sys.argv[0])).replace('clicol-','');

    if cmd == 'test' and len(sys.argv)>1:
        # Print starttime:
        print "Starttime: %s s" % (round(time.time()-starttime,3))
        # Sanity check on colormaps
        cmbuf=list()
        for cm in cmap:
            if cm[4] in cmbuf:
                print "Duplicate pattern:"+repr(cm)
            else:
                cmbuf.append(cm[4])
        if len(sys.argv)>1:
            for test in filter(lambda x: re.match(sys.argv[1],x) and re.match(regex,x), cmaps.sections()):
                test_d=dict(cmaps.items(test))
                try:
                    print test+":"+ofilter(test_d['example'].replace('\'','')+'\n')
                    if test_d['debug'] == "1":
                        print repr(test_d['regex'])
                        print repr(test_d['replacement'])

                except:
                    pass
    elif cmd == 'file' and len(sys.argv)>1:
        try:
            f=open(sys.argv[1],'r')
        except:
            print "Error opening "+sys.argv[1]
            raise
        for line in f:
            print ofilter(line.replace("\n","\r\n").decode('string_escape')), # convert to CRLF to support files created in linux
        f.close()
    elif cmd == 'telnet' or cmd == 'ssh' or (cmd == 'cmd' and len(sys.argv)>1):
        try:
            args = sys.argv[1:]
            if cmd == 'cmd':
                cmd  = sys.argv[1]
                args = sys.argv[2:]
            conn = pexpect.spawn(cmd,args,timeout=1)
        except Exception, e :
            if cmd != 'telnet' and cmd != 'ssh':
                print "Error starting %s" % cmd
                return
        try:
            # Start timeoutcheck to check timeout or string stuck in buffer
            tc = threading.Thread(target=timeoutcheck,args=(config.getfloat("clicol","maxwait"),))
            tc.daemon = True
            tc.start()
            while conn.isalive():
                #esc code table: http://jkorpela.fi/chars/c0.html
                #\x1c = CTRL-\
                conn.interact(escape_character='\x1c',output_filter=ofilter,input_filter=ifilter)
                if is_break:
                    is_break = False
                    print "\r"+" "*100+"\rCLICOL: q:quit,p:pause,F1-12,SF1-8:shortcuts,h-help",
                    command=getCommand()
                    if command=="D":
                        debug += 1
                        if debug > 2:
                            debug=0
                    if command=="p":
                        pause = 1 - pause
                    if command=="q":
                        conn.close()
                        break
                    if command=="h":
                        printhelp(shortcuts)

                    print "\r"+" "*100+"\r"+colorize(lastline,"prompt"), # restore last line/prompt

                    for (key,value) in shortcuts:
                        if command.upper()==key.upper():
                            conn.send(value.decode('string_escape').strip(r'"')) # decode to have CRLF as it is and remove ""
                            break
        except OSError:
            conn.close()
        except Exception, e :
            if debug:
                import traceback
                print traceback.format_exc() # DEBUG
            print e
            print "Error while running "+cmd+" "+str.join(' ',args)

        # Stop timeoutcheck thread and exit
        RUNNING=False
        tc.join()
        if len(buffer)>0: print colorize(buffer), # print remaining buffer
    else:
        print "CLICOL - CLI colorizer and more... Version %s" % __version__
        print "Usage: clicol-{telnet|ssh} [--c {colormap}] [args]"
        print "Usage: clicol-file         [--c {colormap}] {inputfile}"
        print "Usage: clicol-cmd          [--c {colormap}] {command} [args]"
        print "Usage: clicol-test         {colormap regex name (e.g.: '.*' or 'cisco_if|juniper_if')}"
        print
        print "Usage while in session"
        print "Press break key CTRL-\\"
        print
        printhelp(shortcuts)

# END OF PROGRAM
if __name__ == "__main__":
    main()
