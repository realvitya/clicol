import re
import string

def init(ct):
  #Constants for regex loop
  BREAK=True
  CONT =False
  DEBUG=True
  #Beginning of line. Can be empty or couple of backspaces.
  # extra care should be taken as this is a matching group!
  BOL=r"(^[\b\ ]*)"
  #Beginning of a string. Can be empty or default color.
  # this will be cleared from output as this is nonmatching group!
  BOS=string.replace("(?:"+ct['default']+r'|\b)',r'[','\[');

  cmap=[
      #Fields:
      #matcher:
      #effect, dependency, regex
      #replacer:
      #effect, dependency, regex, replacement, break, [debug]

      # Privileged prompt
      # \1: actual prompt
      # \2: anything after prompt (usually when hitting ?
      ["prompt","",re.compile(r"^([a-zA-Z0-9\/_@\-\(\)]+#)([^\r\n]*)$",flags=re.M), ct['privprompt']+r"\1"+ct['default']+r"\2",BREAK],
      # Non-privileged prompt
      ["prompt","",re.compile(r"^([a-zA-Z0-9\/_@\-\(\)]+(?:>|\$))([^\r\n]*)$",flags=re.M), ct['nonprivprompt']+r"\1"+ct['default']+r"\2",BREAK],

      # Pager (more)
      ["","",re.compile(r"^(.*-+\ *\(?[mM][oO][rR][eE](?:\ [0-9]+\%)?\)?\ *[->]+)(.*)$",flags=re.M), ct['pager']+r"\1"+ct['default']+r"\2",BREAK],

      #Traffic
      ["","",re.compile(BOS+r"(drop.*)([1-9]+ )(pkts\/sec)\b",flags=re.M),r"\1"+ct['lowalert']+r"\2"+ct['default']+r"\3",CONT],
      ["","",re.compile(BOS+r"([1-9]+ )((?:bits|bytes|pkts)\/sec)\b",flags=re.M),ct['trafficrate']+r"\1"+ct['default']+r"\2",CONT],

      #MAC address
      ["","",re.compile(BOS+r"((?:[a-f0-9]{2}[:-]){5}[a-f0-9]{2})",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:[a-f0-9]{4}\.){2}[a-f0-9]{4})",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      #IPv4 address
      ["","",re.compile(BOS+r"((?:[0-9]{1,3}\.){3}[0-9]{1,3})",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      #IPv6 address
      ["","",re.compile(BOS+r"((?:(?:(?:[0-9A-Fa-f]{1,4}:){7}(?:[0-9A-Fa-f]{1,4}|:))|(?:(?:[0-9A-Fa-f]{1,4}:){6}(?::[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){5}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,2})|:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){4}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,3})|(?:(?::[0-9A-Fa-f]{1,4})?:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){3}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,4})|(?:(?::[0-9A-Fa-f]{1,4}){0,2}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){2}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,5})|(?:(?::[0-9A-Fa-f]{1,4}){0,3}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){1}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,6})|(?:(?::[0-9A-Fa-f]{1,4}){0,4}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?::(?:(?:(?::[0-9A-Fa-f]{1,4}){1,7})|(?:(?::[0-9A-Fa-f]{1,4}){0,5}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))))",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],

      #Interface description
      ["","",re.compile(BOL+r"(\ *[dD]escription:?\ .+)$",flags=re.M),r"\1"+ct['description']+r"\2"+ct['default'],BREAK],
      #no shutdown
      ["","",re.compile(r"\b(no shutdown)\b",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],
      ["","",re.compile(r"\b(?<!no )(shutdown)\b",flags=re.M),ct['alert']+r"\1"+ct['default'],CONT],

      #banner
      ["","",re.compile(BOL+r"(\ {0,2}\*\*+.*)$",flags=re.M),r"\1"+ct['comment']+r"\2"+ct['default'],CONT],
     ]
  return cmap
