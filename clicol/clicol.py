#!/usr/bin/python

import os, sys, re
import string
import pexpect
import ConfigParser
from importlib import import_module

buffer = ''
effects = set()
ct = dict()
cmap = list()
wait = 0
INTERACT=re.compile(r".*(?:\r\n|[\]\)\:\>\#\$-]\ *)$",flags=re.S)

def colorize(text):
 global effects, cmap
 colortext=""
 for line in text.splitlines(True): 
   for i in cmap:
      matcher=False
      try: 
        effect=i[0] # invokes other rules
        dep   =i[1]
        reg   =i[2]
        rep   =i[3]
        break_=i[4]
        debug =i[5]
      except IndexError:
        if len(i) == 3:
           #this is a matcher
           matcher=True
        elif len(i) == 5:
           #don't have DEBUG
           debug=False
        else:
           raise
      if len(dep)>0 and dep not in effects: # we don't meet our dependency
         continue # move on to the next regex
      if matcher:
         if reg.match(line):
            effects.add(effect)
         continue
      origline=line
      line=reg.sub(rep,origline)
      if debug:
         print repr(line), repr(effects)
      if line != origline: # we have a match
         if len(effect)>0: # we have an effect
            effects.add(effect)
         if 'prompt' in effects: #prompt eliminates all effects
            effects=set()
         if break_:
            break
   colortext+=line
 return colortext

def ofilter(input):
   global buffer
   global wait
   
   # If not ending with linefeed we are interacting or buffering
   if not INTERACT.match(input):
      #special characters. e.g. moving cursor
      lastline=input.rpartition('\r\n')[2]
      if re.match(r"[\b]",lastline):
        buffer=""
        wait = 0
        return colorize(input)
      #collect the input into buffer
      buffer += input
      if len(buffer)<80: # most likely interactive prompt
         bufout=buffer
         buffer = ""
         wait = 0
         return colorize(bufout)
      else:
         #Waiting for more input
         if wait > 1: # Waited enough. To be on the safe side we print out
             wait=0
             bufout = buffer+input
             buffer = ""
             return colorize(bufout)
         else:
             wait+=1
             return ""
   else:
       #Got linefeed, dump buffer
       #
       # BUG: sometimes after exiting, several extra linefeed. seems to be pexpect bug.
       bufout = buffer+input
       buffer = ""
       wait = 0
       return colorize(bufout)

def main():
    global ct, cmap

    config = ConfigParser.SafeConfigParser({'background': 'dark',
                                            'regex': 'common,cisco'})
    config.add_section('clicol')
    config.read(['/etc/clicol.cfg', 'clicol.cfg', os.path.expanduser('~/clicol.cfg')])
    bg = config.get('clicol','background')
    if bg == "dark":
        import ct_dark as colortables
    elif bg == "light":
        import ct_light as colortables
    else:
        print "No such colortable: "+bg
        exit(1)
    ct = colortables.ct

    regex = set(str(config.get('clicol','regex')).split(','))
    for cm in regex:
        if cm in ["common","cisco","juniper"]:
            cmod=import_module("cm_"+cm)
            cmap.extend(cmod.init(ct))
    #Check how we were called
    # valid options: clicol-telnet, clicol-ssh, clicol-test
    cmd = str(os.path.basename(sys.argv[0])).replace('clicol-','');
    if cmd == 'test' and len(sys.argv)>1:
        #Sanity check on colormaps
        cmbuf=list()
        for cm in cmap:
            if cm[2] in cmbuf:
                print "Duplicate pattern:"+repr(cm)
            else:
                cmbuf.append(cm[2])
        try:
            f=open(sys.argv[1],'r')
        except:
            print "Error opening "+sys.argv[1]
            raise
        for line in f:
            print ofilter(line),
        f.close()
    elif cmd == 'telnet' or cmd == 'ssh':
        try:
            c = pexpect.spawn(cmd,sys.argv[1:])
            c.interact(output_filter=ofilter)
        except:
            print "Error running "+cmd+" "+str.join(' ',sys.argv[1:])
    else:
        print "Usage: clicol-[telnet|ssh] [args]"
        print "Usage: clicol-test {inputfile}"

main()
