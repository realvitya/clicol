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
      # Hostname in configuration
      ["","",re.compile(BOL+r"(hostname )([a-zA-Z0-9_-]+)",flags=re.M),r'\1\2'+ct['privprompt']+r'\3'+ct['default'],CONT],
      #interface keyword
      ["","",re.compile(BOL+r"(interface )",flags=re.M),ct['general_configitem']+r"\1\2"+ct['default'],CONT],
      #interface names (long ethernet)
      ["","",re.compile(BOS+r"((?:[fF]ourty|[tT]en)?(?:[gG]igabit|[fF]ast)?[eE]thernet[0-9]+(?:[\/\.:][0-9]+)*[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:[Mm]anagement[0-9]+(?:[\/\.:][0-9]+)*[,:]?))",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"\b(?<![\(\)\[\]\\\/.-])([efgtEFGTmM][aie]*[0-9]{1,4}(?:[\/.:][0-9]{1,4})*[,:*]?)\b(?! -)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:ATM|nvi|[pP]ort-channel|[sS]e(rial)?|[pP]o|vfc|BRI|Dialer)[0-9\/:,.]+[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"((?:[Mm]ulti|[lL]o|[Tt]u|[Mm]gmt|[Nn]ull|[vV]lan)(link|opback|nnel)?[0-9]+,?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOL+r"((line)\ (con\ ?[0-9]?|vty [0-9]+(?: [0-9]+)?|aux [0-9]+|console))",flags=re.M),r"\1"+ct['interface']+r"\2"+ct['default'],CONT],

      #interface stats
      ["","",re.compile(r"([1-9]+ )(runts|giants|throttles|(?:input|output) errors|CRC|frame|overrun|ignored|watchdog|input packets with dribble|underruns|collisions|interface resets|unknown protocol drops|babbles|late collision|deferred|lost carrier|no carrier|output buffer)",flags=re.M),ct['alert']+r"\1\2"+ct['default'],CONT],

      #Duplex
      ["","",re.compile(BOS+r"([hH]alf[\ -]?[dD]uplex)",flags=re.M),ct['lowalert']+r"\1"+ct['default'],CONT],
      ["","",re.compile(BOS+r"([fF]ull[\ -]?[dD]uplex)",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],

      #show interface status
      ["","",re.compile(BOL+r"(.*\ +.*\ +)(notconnect)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['lowalert']+r"\3"+ct['default']+r"\4",CONT],
      ["","",re.compile(BOL+r"(.*\ +.*\ +)(connected)(\ +.*\ +.*)$",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default']+r"\4",CONT],

      #interface configuration
      ["","",re.compile(BOL+r"(switchport mode )(.*)$",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],
      ["","",re.compile(BOL+r"(switchport trunk allowed vlan )(.*)$",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default'],BREAK],

      #show ver
      ["","",re.compile(BOL+r"((?:.*\buptime|.*\brestarted|Last reload).*)",flags=re.M),r"\1"+ct['general_value']+r"\2"+ct['default'],BREAK],
      ["","",re.compile(BOL+r"(.*\b(?:Configuration register|System image file) is )(.*)",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],

      #IOS router ping
      ["ping","",re.compile(BOS+r"[sS]ending [0-9]+",flags=re.M)], # only turns on ping effect
      #'.' and '!' means loss or received packets
      ["","ping",re.compile(r"^(\.\r?\n?)$",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],
      ["","ping",re.compile(r"^(\!+\r?\n?)$",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],
      # Reload confirmation
      ["","",re.compile(r"^(Proceed with reload\?)( \[confirm\].*)$",flags=re.M),ct['highalert']+r"\1"+ct['default']+r"\2",BREAK],

      # show log
      ["","",re.compile(r"(%.+-[0-3]-[0-9A-Z]+)(:)",flags=re.M),ct['alert']+r"\1"+ct['default']+r"\2",CONT],
      ["","",re.compile(r"(%.+-4-[0-9A-Z]+)(:)",flags=re.M),ct['lowalert']+r"\1"+ct['default']+r"\2",CONT],
      #["","",re.compile(r"(%.+-[5-9]-[0-9A-Z]+)(:)",flags=re.M),ct['alert']+r"\1"+ct['default']+r"\2",CONT],

      # ASA show failover
      ["","",re.compile(BOL+r"(Last failover at )(.*)",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],
      ["","",re.compile(r"(?<=\): )(Normal \((?:Not-)?Monitored\))",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],
      ["","",re.compile(r"(?<=\): )(Normal )(\(Waiting\))",flags=re.M),ct['good']+r"\1"+ct['lowalert']+r"\2"+ct['default'],BREAK],
      ["","",re.compile(r"(?<=\): )(Failed(?: \(.*)?)",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],

      # ASA show run access-list
      #  remark
      ["","",re.compile(BOL+r"(access-list [0-9a-zA-Z_-]+ )(remark .*)",flags=re.M),r"\1\2"+ct['comment']+r"\3"+ct['default'],BREAK],

     ]
  return cmap
