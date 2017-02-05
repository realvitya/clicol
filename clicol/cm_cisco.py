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
  BOS=string.replace("(?:"+ct['default']+")?",r'[','\[');

  cmap=[
      #Fields:
      #matcher:
      #effect, dependency, regex
      #replacer:
      #effect, dependency, regex, replacement, break, [debug]
      # Hostname in configuration
      ["","",re.compile(BOL+r"(hostname )([a-zA-Z0-9_-]+)",flags=re.M),r'\1\2'+ct['privprompt']+r'\3'+ct['default'],CONT],
      #interface keyword
      ["","",re.compile(BOL+r"(interface )",flags=re.M),ct['general_configitem']+r"\1\2"+ct['default'],CONT],
      #interface names (long ethernet)
      ["","",re.compile(BOS+r"((?:[fF]ourty|[tT]en)?(?:[gG]igabit|[fF]ast)?[eE]thernet[0-9]+(?:[\/\.:][0-9]+)*[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"\b([efgtEFGT][aie]*[0-9]{1,4}(?:[\/.:][0-9]{1,4})*[,:*]?)\b(?! -)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:ATM|nvi|[pP]ort-channel|[sS]e(rial)?|[pP]o|vfc|BRI|Dialer)[0-9\/:,.]+[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:[Mm]ulti|[lL]o|[Tt]u|[Mm]gmt|[Nn]ull|[vV]lan)(link|opback|nnel)?[0-9]+,?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOL+r"((line)\ (con\ ?[0-9]?|vty [0-9]+(?: [0-9]+)?|aux [0-9]+|console))",flags=re.M),r"\1"+ct['interface']+r"\2"+ct['default'],CONT],

      #interface stats
      ["","",re.compile(r"([1-9]+ )(runts|giants|throttles|(?:input|output) errors|CRC|frame|overrun|ignored|watchdog|input packets with dribble|underruns|collisions|interface resets|unknown protocol drops|babbles|late collision|deferred|lost carrier|no carrier|output buffer)",flags=re.M),ct['alert']+r"\1\2"+ct['default'],CONT],

      #Duplex
      ["","",re.compile(BOS+r"([hH]alf[\ -]?[dD]uplex)",flags=re.M),ct['lowalert']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"([fF]ull[\ -]?[dD]uplex)",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],

#      #Traffic
#      ["","",re.compile(BOL+r"(.*(?:minute|second)(?:\ [io][nu]t?put\ rate\ ))([0-9]+)(.*)",flags=re.M),r"\1\2"+ct['trafficrate']+r"\3"+ct['default']+r"\4",CONT],
#      ["","",re.compile(BOL+r"(.*(?:minute|second)(?: drop rate ))([0-9]+)(.*)",flags=re.M),r"\1\2"+ct['droprate']+r"\3"+ct['default']+r"\4",CONT],

      #show interface status
      ["","",re.compile(BOL+r"(.*\ +.*\ +)(notconnect)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['lowalert']+r"\3"+ct['default']+r"\4",CONT],
      ["","",re.compile(BOL+r"(.*\ +.*\ +)(connected)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default']+r"\4",CONT],

      #IOS router ping
      ["ping","",re.compile(BOS+r"[sS]ending [0-9]+",flags=re.M)], # only turns on ping effect
      #'.' and '!' means loss or received packets
      ["","ping",re.compile(r"^(\.\r?\n?)$",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],
      ["","ping",re.compile(r"^(\!+\r?\n?)$",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],
      # Reload confirmation
      ["","",re.compile(r"^(Proceed with reload\?)( \[confirm\].*)$",flags=re.M),ct['highalert']+r"\1"+ct['default']+r"\2",BREAK],
     ]
  return cmap
