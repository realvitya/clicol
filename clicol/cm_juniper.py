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
  BOL=r"(^[\b\ ]+(?<! )|^)"
  #Beginning of a string. Can be empty or default color.
  BOS=string.replace("(?:"+ct['default']+r'|\b)',r'[',r'\[');

  cmap=[
      #Fields:
      #matcher:
      #priority, effect, dependency, regex
      #replacer:
      #priority, effect, dependency, regex, replacement, break, [debug]

      #Juniper prompt user@hostname>
      [4,"prompt","",re.compile(r"(?i)^((?:[\b]+\ *[\b]*)?[a-z0-9\/_\-]+@[a-z0-9\/_\-]*(?:>|\$) )(.*)$",flags=re.M), ct['privprompt']+r"\1"+ct['default']+r"\2",BREAK],

      # interface names
      [15,"","",re.compile(BOS+r"\b(?<![\(\)\[\]\\\/.-:])((?:(?:(?:[gx]e|gr|ip|[lmuv]t|p[de]|pf[eh]|lc|lsq|sp)-|ae|em|fxp|lo|lis|me|pip|pp)[0-9]{1,4}|(?:reth|irb|cbp|lsi|mtun|pim[de]|tap|dsc|demux)[0-9]?)(?:[\/.][0-9]{1,5})*)\b(?! -)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],

      #BGP
      # Juniper show bgp sum
      #Groups: 8 Peers: 17 Down peers: 0
      [20,"","",re.compile(BOL+r"(Groups: [0-9]+ Peers: [0-9]+ Down peers: )(0)",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default'],CLEAR],
      [20,"","",re.compile(BOL+r"(Groups: [0-9]+ Peers: [0-9]+ Down peers: )([0-9]+)",flags=re.M),r"\1\2"+ct['alert']+r"\3"+ct['default'],CLEAR],
      # Established
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9ywdh: ]+)(\ +Establ.*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['important_value']+r"\3"+ct['default']+r"\4"+ct['general_value']+r"\5"+ct['good']+r"\6"+ct['default'],CLEAR],
      # from neighbor
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9ywdh:]+)(\ +(?:[0-9]+\/)+.*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['important_value']+r"\3"+ct['default']+r"\4"+ct['general_value']+r"\5"+ct['good']+r"\6"+ct['default'],CLEAR],
      # Active, Connect, or Idle
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9ywdh]+)(\ +(?:Active|Connect|Idle).*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['important_value']+r"\3"+ct['default']+r"\4"+ct['general_value']+r"\5"+ct['alert']+r"\6"+ct['default'],CLEAR],
      # Session timeout warning
      [20,"timeoutwarn","",re.compile(BOL+r"\x07Warning: session will be closed in [0-9]{1,2} (?:minutes?|seconds) if there is no activity.*")],
     ]
  return cmap
