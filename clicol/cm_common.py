import re
import string

def init(ct):
  #Constants for regex loop
  #options:
  CLEAR=2
  BREAK=1
  CONT =0

  DEBUG=True
  #Beginning of line. Can be empty or couple of backspaces.
  # extra care should be taken as this is a matching group!
  BOL=r"(^[\b\ ]+(?<! )|^)"
  #Beginning of a string. Can be empty or default color.
  # this will be cleared from output as this is nonmatching group!
  BOS=string.replace("(?:"+ct['default']+r'|\b)',r'[','\[');

  cmap=[
      #Fields:
      #matcher:
      #priority, effect, dependency, regex
      #replacer:
      #priority, effect, dependency, regex, replacement, options, [debug]

      # Privileged prompt
      # \1: actual prompt
      # \2: anything after prompt (usually when hitting ?
      [5,"prompt","",re.compile(r"^((?:[\b]+\ *[\b]*)?[a-zA-Z0-9\/_@\-\(\)]+#)(.*)$",flags=re.M), ct['privprompt']+r"\1"+ct['default']+r"\2",BREAK],
      # Non-privileged prompt
      [5,"prompt","",re.compile(r"^((?:[\b]+\ *[\b]*)?[a-zA-Z0-9\/_@\-\(\)]+(?:>|\$))(.*)$",flags=re.M), ct['nonprivprompt']+r"\1"+ct['default']+r"\2",BREAK],

      # Pager (more)
      # CONT because sometimes there is output after 'more'
      [5,"more","",re.compile(r"^([\b ]*[<-]+\ *\(?[mM][oO][rR][eE](?:\ [0-9]+\%)?\)?\ *[->]+\ ?)(.*)$",flags=re.M), ct['pager']+r"\1"+ct['default']+r"\2",CONT],

      #Traffic
      [10,"","",re.compile(BOS+r"(drop.*)([1-9][0-9]* )((?:packets|pkts)\/sec)\b",flags=re.M),r"\1"+ct['lowalert']+r"\2"+ct['default']+r"\3",CONT],
      [10,"","",re.compile(BOS+r"([1-9][0-9]* )((?:bits|bytes|pkts|packets)\/sec)\b",flags=re.M),ct['trafficrate']+r"\1"+ct['default']+r"\2",CONT],

      #MAC address
      [10,"","",re.compile(BOS+r"(?<![:-])\b((?:[a-fA-F0-9]{2}[:-]){5}[a-fA-F0-9]{2})\b(?![:-])",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      [10,"","",re.compile(BOS+r"(?<!\.)\b((?:[a-fA-F0-9]{4}\.){2}[a-fA-F0-9]{4})\b(?!\.)",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      #IPv4 address
      [10,"","",re.compile(BOS+r"(?<![0-9]\.)\b((?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\/[0-9]{1,2})?)\b(?!\.[0-9])",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],
      #IPv6 address
      [10,"","",re.compile(BOS+r"((?:(?:(?:[0-9A-Fa-f]{1,4}:){7}(?:[0-9A-Fa-f]{1,4}|:))|(?:(?:[0-9A-Fa-f]{1,4}:){6}(?::[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){5}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,2})|:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(?:(?:[0-9A-Fa-f]{1,4}:){4}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,3})|(?:(?::[0-9A-Fa-f]{1,4})?:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){3}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,4})|(?:(?::[0-9A-Fa-f]{1,4}){0,2}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){2}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,5})|(?:(?::[0-9A-Fa-f]{1,4}){0,3}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?:(?:[0-9A-Fa-f]{1,4}:){1}(?:(?:(?::[0-9A-Fa-f]{1,4}){1,6})|(?:(?::[0-9A-Fa-f]{1,4}){0,4}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(?::(?:(?:(?::[0-9A-Fa-f]{1,4}){1,7})|(?:(?::[0-9A-Fa-f]{1,4}){0,5}:(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))(?:\/[0-9]{1,3})?)\b",flags=re.M), ct['address']+r"\1"+ct['default'],CONT],

      #Interface description
      [10,"","",re.compile(BOL+r"(\ *[dD]escription:?\ .+)$",flags=re.M),r"\1"+ct['description']+r"\2"+ct['default'],BREAK],
      #no shutdown
      [10,"","",re.compile(r"\b(no shutdown)\b",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],
      [10,"","",re.compile(r"\b(?<!no )(shutdown)\b",flags=re.M),ct['alert']+r"\1"+ct['default'],CONT],

      # admin down
      [10,"","",re.compile(BOS+r"(admin(?:istratively)? down)",flags=re.M),ct['alert']+r"\1"+ct['default'],CONT],
      [10,"","",re.compile(BOS+r"(disabled|\b[dD]own\b)",flags=re.M),ct['alert']+r"\1"+ct['default'],CONT],
      [10,"","",re.compile(BOS+r"(enabled|\b[uU]p\b)",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],


      #banner
      [10,"","",re.compile(BOL+r"( *\*[\*\ ]+.*\*\ *[\r\n]?)$",flags=re.M),r"\1"+ct['comment']+r"\2"+ct['default'],BREAK],
     ]
  return cmap
