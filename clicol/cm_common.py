import re

#Constants for regex loop
BREAK=True
CONT =False
DEBUG=True
#Beginning of line. Can be empty or couple of backspaces.
BOL=r"(^[\b\ ]*)"

def init(ct):
  cmap=[
      #Fields:
      #matcher:
      #effect, dependency, regex
      #replacer:
      #effect, dependency, regex, replacement, break, [debug]
      ["prompt","",re.compile(r"^([a-zA-z\-0-9]+[\(\)>#\$\ ]$)",flags=re.M),ct['prompt']+r"\1"+ct['default'],BREAK],
      #PING section
      #IOS router ping
      ["ping","",re.compile(r"[sS]ending [0-9]+",flags=re.M)], # only turns on ping effect
      #'.' and '!' means loss or received packets
      ["","ping",re.compile(r"^(\.\r?\n?)$",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],
      ["","ping",re.compile(r"^(\!+\r?\n?)$",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],
      #/PING section
     ]
  return cmap
