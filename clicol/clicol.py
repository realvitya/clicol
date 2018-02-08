#!/usr/bin/python

import os, sys, re
import string
import pexpect
import ConfigParser
import timeit
import threading
import time
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
#Interactive regex matches for
# - prompt (asd# ) (all)
# - question ([yes]) (cisco)
# - more (-more-) (cisco,juniper)
# - restore coloring (\x1b[m) (linux)
# possible chars: "\):>#$/- "
#INTERACT=re.compile(r"(?i)^([^ ]*([\]\>\#\$][: ]?)(.*)| ?-+\(?more(?: [0-9]{1,2}%)?\)?-+ ?|\x1b\[m|username: ?|password: ?)$",flags=re.S)
INTERACT=re.compile(r"(?i)^(" # START of whole line matches
                     "[^ ]*([\]\>\#\$][: ]?)(.*)" # prompt
                     "| ?<?-+ ?\(?more(?: [0-9]{1,2}%)?\)? ?-+>? ?([\b ]+)?" # more (\b can be at the end when excessive enters are pressed
                     "|\x1b\[m"                   # color escape sequence
                     "|username: ?"
                     "|password: ?"
                     ")$"                         # END of whole line match
                     "|\]:? ?$" # probably question (reload? [yes])
                     ,flags=re.S)

def timeoutcheck():
    global timeout, maxtimeout
    
    while True:
        time.sleep(1)
        if maxtimeout<=0: continue # timeout disabled
        if timeout>=maxtimeout:
            preventtimeout()       # send something to prevent timeout on device
            timeout=0
        else:
            timeout += 1

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
   for i in cmap:
      cmap_counter+=1
      matcher=False
      try: 
        prio  =i[0] # priority
        effect=i[1] # invokes other rules
        dep   =i[2] # dependency on effect
        reg   =i[3] # regexp match string
        rep   =i[4] # replacement string
        option=i[5] # match options (continue,break,clear)
        cdebug=i[6] # debug
      except IndexError:
        if len(i) == 4:
           #this is a matcher
           matcher=True
        elif len(i) == 6:
           #don't have debug
           cdebug=False
        else:
           raise
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
      line=reg.sub(rep,origline)
      if cdebug:
         print "\r\n\033[38;5;208mD-",repr(origline), repr(line), repr(effects), "\033[0m\r\n" # debug
      if line != origline: # we have a match
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
   if not is_break: timeout=0; prevents=0
   return input

def ofilter(input):
   global buffer
   global pause # coloring must be paused
   global lastline
   global debug

   # Coloring is paused by escape character
   if pause:
       return input
   
   # If not ending with linefeed we are interacting or buffering
   if not (input[-1]=="\r" or input[-1]=="\n"):
      if debug: print "\r\n\033[38;5;208mI-",repr(input),"\033[0m\r\n" # DEBUG
      lastline=input.splitlines()[-1]
      if debug: print "\r\n\033[38;5;208mL-",repr(lastline),"\033[0m\r\n" # DEBUG
      #special characters. e.g. moving cursor
      #if input not starts with \b then it's sg like more or anything device wants to hide.
      #regular text can follow which we want to colorize
      if ("\a" in lastline or "\b" in lastline) and (lastline[0]!="\a" and lastline[0]!="\b") and input==lastline:
        buffer=""
        return colorize(input,["prompt"])
      #collect the input into buffer
      buffer += input
      if debug: print "\r\n\033[38;5;208mB-",repr(buffer),"\033[0m\r\n" # DEBUG
      if INTERACT.search(lastline): # prompt or question at the end
         bufout=buffer
         buffer = ""
         return colorize(bufout)
        
      if len(buffer)<100:  # interactive or end of large chunk
         bufout=buffer
         if "\r" in input or "\n" in input: # multiline input, not interactive
           return ""
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
            buffer=lastline
            return colorize(bufout)
   else:
       if debug: print "\r\n\033[38;5;208mNI-",repr(input),"\033[0m\r\n" # DEBUG
       #Got linefeed, dump buffer
       bufout = buffer+input
       buffer = ""
       return colorize(bufout)

def main():
    global conn, ct, cmap, pause, timeoutact, terminal, buffer, lastline, debug
    global maxtimeout, maxprevents
    default_config={'colortable' :r'dbg_net',
                                                'terminal'   :r'securecrt',
                                                'regex'      :r'all',
                                                'timeoutact' :r'true',
                                                'debug'      :r'0',
                                                'maxtimeout' :r'0',
                                                'maxprevents':r'0',
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
    if cct == "dbg_net":
        import ct_dbg_net as colortables
    elif cct == "lbg_net":
        import ct_lbg_net as colortables
    else:
        print "No such colortable: "+cct
        exit(1)
    ct = colortables.ct


    #Check how we were called
    # valid options: clicol-telnet, clicol-ssh, clicol-test
    cmd = str(os.path.basename(sys.argv[0])).replace('clicol-','');

    regex = set(str(config.get('clicol','regex')).split(','))
    try:
        if len(sys.argv)>1 and sys.argv[1] == '--c': # called with specified colormap
            regex = sys.argv[2].split(",") # input is in "cisco,juniper,..." format
            del sys.argv[1] # remove --c from args
            del sys.argv[1] # remove colormap string from args
    except: # index error, wrong call
        cmd = 'error'
    if "all" in regex:
        regex = ["common","cisco","juniper"]
    for cm in regex:
        if cm in ["common","cisco","cisco_show","juniper"]:
            cmod=import_module("clicol.cm_"+cm)
            cmap.extend(cmod.init(ct))
    cmap.sort(key=lambda match: match[0]) # sort colormap based on priority
    if cmd == 'test' and len(sys.argv)>1:
        #Sanity check on colormaps
        cmbuf=list()
        for cm in cmap:
            if cm[3] in cmbuf:
                print "Duplicate pattern:"+repr(cm)
            else:
                cmbuf.append(cm[3])
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
            if maxtimeout>0: # enable this feature
                tc = threading.Thread(target=timeoutcheck)
                tc.daemon = True
                tc.start()
            while conn.isalive():
                #esc code table: http://jkorpela.fi/chars/c0.html
                #\x1c = CTRL-\
                conn.interact(escape_character='\x1c',output_filter=ofilter,input_filter=ifilter)
                if is_break:
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
        print colorize(buffer) # print remaining buffer
    else:
        print "CLICOL - CLI colorizer and more... Version %s" % __version__
        print "Usage: clicol-{telnet|ssh} [--c {colormap}] [args]"
        print "Usage: clicol-test         [--c {colormap}] {inputfile}"
        print "Usage: clicol-cmd          [--c {colormap}] {command} [args]"
        print
        print "Usage while in session"
        print "Press break key CTRL-\\"
        print
        printhelp(shortcuts)

# END OF PROGRAM
