import re
import string

def init(ct):
  #Constants for regex loop
  BREAK=True
  CONT =False
  DEBUG=True
  #Beginning of line. Can be empty or couple of backspaces.
  BOL=r"(^[\b\ ]*)"
  #Beginning of a string. Can be empty or default color.
  BOS=string.replace("(?:"+ct['default']+r'|\b)',r'[',r'\[');

  cmap=[
      #Fields:
      #matcher:
      #effect, dependency, regex
      #replacer:
      #effect, dependency, regex, replacement, break, [debug]

      # no juniper specific rules yet
     ]
  return cmap
