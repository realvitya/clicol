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

def colorize(text):
 global effects, cmap
 #global DEFCOLOR
 colortext=""
 for line in text.splitlines(True): 
   #print repr(line)
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
            #print repr(effects)
         continue
      origline=line
      line=reg.sub(rep,origline)
      if debug:
         print repr(line), repr(effects)
      if line != origline: # we have a match
         if len(effect)>0: # we have an effect
            effects.add(effect)
         #print repr(effects)
         if 'prompt' in effects: #prompt eliminates all effects
            effects=set()
         if break_:
            break
   colortext+=line
 return colortext

def ofilter(input):
   global buffer
   global effects
   
   # If not ending with linefeed we are interacting
   if not re.match(r".*(\n|\r\n)",input,flags=re.M):
      #special characters. e.g. moving cursor
      if not input.isalnum():
         return colorize(input)
      #collect the input into buffer
      buffer += input
      #Buffer too small, this shall be a oneline question or user echo
      if len(buffer) < 200:
         buffer = ""
         return colorize(input)
      else:
         #Waiting for more input
         return ""
   else:
      #Got linefeed, dump buffer
      bufout = buffer+input
      buffer = ""
      return colorize(bufout)

def main():
    global ct, cmap

    config = ConfigParser.SafeConfigParser({'background': 'dark',
                                            'regex': 'common,cisco'})
    config.add_section('clicol')
    config.read(['/etc/clicol.cfg', 'clicol.cfg', os.path.expanduser('~/clicol.cfg')])
    #print config.get('clicol','background')
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
        c = pexpect.spawn(cmd,sys.argv[1:])
        c.interact(output_filter=ofilter)
    else:
        print "Usage: clicol-[telnet|ssh] [args]"
        print "Usage: clicol-test {inputfile}"

main()
