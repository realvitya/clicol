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
  BOL=r"(^.*[\b\ ]+(?<! )|^)"
  #Beginning of a string. Can be empty or default color.
  BOS=string.replace("(?:"+ct['default']+r'|\b)',r'[',r'\[');

  cmap=[
      #Fields:
      #matcher:
      #priority, effect, dependency, regex
      #replacer:
      #priority, effect, dependency, regex, replacement, options, [debug]

      #interface stats
      [20,"","",re.compile(r"([1-9][0-9]* )(runts|giants|throttles|(?:input|output) errors|CRC|frame|overruns?|ignored|watchdog|input packets with dribble condition detected|underruns?|collisions|interface resets|unknown protocol drops|babbles|late collision|deferred|lost carrier|no carrier|output buffers?(?: failures| swapped out)?)",flags=re.M),ct['alert']+r"\1\2"+ct['default'],CONT],

      #Duplex
      [20,"","",re.compile(BOS+r"([hH]alf[\ -]?[dD]uplex)",flags=re.M),ct['lowalert']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"([fF]ull[\ -]?[dD]uplex)",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],

      #show interface status
      [20,"","",re.compile(BOL+r"(.*\ +.*\ +)(notconnect)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['lowalert']+r"\3"+ct['default']+r"\4",CONT],
      [20,"","",re.compile(BOL+r"(.*\ +.*\ +)(connected)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default']+r"\4",CONT],

      #BGP
      # AS number
      [20,"","",re.compile(r"(local AS number )([0-9]+)",flags=re.M),r"\1"+ct['important_value']+r"\2"+ct['default'],CONT],
      # time < 1d
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+)(\ +[46]\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9:]+)(\ +[0-9]+.*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['default']+r"\3"+ct['important_value']+r"\4"+ct['default']+r"\5"+ct['lowalert']+r"\6"+ct['default']+r"\7",CLEAR],
      # time >= 1d
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+)(\ +[46]\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9ywdh]+)(\ +[0-9]+.*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['default']+r"\3"+ct['important_value']+r"\4"+ct['default']+r"\5"+ct['good']+r"\6"+ct['default']+r"\7",CLEAR],
      # Active/Idle
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+)(\ +[46]\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))([0-9ywdh:]+)(\ +(?:Active|Idle).*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['default']+r"\3"+ct['important_value']+r"\4"+ct['default']+r"\5"+ct['alert']+r"\6"+r"\7"+ct['default'],CLEAR],
      # never
      [20,"","",re.compile(BOL+r"((?:[0-9]+\.){3}[0-9]+)(\ +[46]\ +)([0-9]+)((?:\ +[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +)(?:[0-9]+\ +))(never.*)",flags=re.M),r"\1"+ct['address']+r"\2"+ct['default']+r"\3"+ct['important_value']+r"\4"+ct['default']+r"\5"+ct['alert']+r"\6"+ct['default'],CLEAR],

      # certmap tailing space
      [20,"","",re.compile(BOL+r"( subject-name co )(.* )$",flags=re.M),r"\1\2"+ct['highalert']+r"\3"+ct['default'],BREAK],

     ]
  return cmap
