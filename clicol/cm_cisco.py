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
      #interface keyword
      ["","",re.compile(BOL+r"(interface)\ ",flags=re.M),ct['general_configitem']+r"\1\2"+ct['default']+" ",CONT],
      #interface names (long ethernet)
      ["","",re.compile(r"((?:^| )(?:[fF]ast|[gG]igabit|[tT]en[gG]igabit)[eE]thernet(?:[0-9]+[/\.]?)+)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
     ]
  return cmap
