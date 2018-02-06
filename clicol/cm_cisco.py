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
      #priority, effect, dependency, regex, replacement, options, [debug]
      # Hostname in configuration
      [20,"","",re.compile(BOL+r"(hostname )([a-zA-Z0-9_-]+)",flags=re.M),r'\1\2'+ct['privprompt']+r'\3'+ct['default'],CONT],
      #interface keyword
      [20,"","",re.compile(BOL+r"(interface )",flags=re.M),ct['general_configitem']+r"\1\2"+ct['default'],CONT],
      #interface names (long ethernet)
      [20,"","",re.compile(BOS+r"((?:[fF]ourty|[tT]en)?(?:[gG]igabit|[fF]ast)?[eE]thernet[0-9]+(?:[\/\.:][0-9]+)*[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"((?:[Mm]anagement[0-9]+(?:[\/\.:][0-9]+)*[,:]?))",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"\b(?<![\(\)\[\]\\\/.-:])([efgtEFGTmM][aie]*[0-9]{1,4}(?:[\/.:][0-9]{1,4})*[,:*]?)\b(?! -)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"((?:ATM|nvi|[pP]ort-channel|[sS]e(rial)?|[pP]o|vfc|BRI|Dialer)[0-9\/:,.]+[,:]?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"((?:[Mm]ulti|[lL]o|[Tt]u|[Mm]gmt|[Nn]ull|[vV]l(?:an)?)(link|opback|nnel)?[0-9]+,?)",flags=re.M),ct['interface']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOL+r"((line)\ (con\ ?[0-9]?|vty [0-9]+(?: [0-9]+)?|aux [0-9]+|console))",flags=re.M),r"\1"+ct['interface']+r"\2"+ct['default'],CONT],

      #interface stats
      [20,"","",re.compile(r"([1-9][0-9]* )(runts|giants|throttles|(?:input|output) errors|CRC|frame|overruns?|ignored|watchdog|input packets with dribble condition detected|underruns?|collisions|interface resets|unknown protocol drops|babbles|late collision|deferred|lost carrier|no carrier|output buffers?(?: failures| swapped out)?)",flags=re.M),ct['alert']+r"\1\2"+ct['default'],CONT],

      #Duplex
      [20,"","",re.compile(BOS+r"([hH]alf[\ -]?[dD]uplex)",flags=re.M),ct['lowalert']+r"\1"+ct['default'],CONT],
      [20,"","",re.compile(BOS+r"([fF]ull[\ -]?[dD]uplex)",flags=re.M),ct['good']+r"\1"+ct['default'],CONT],

      #show interface status
      [20,"","",re.compile(r"(\ +.*\ +)(notconnect)(\ +.*\ +.*)$",flags=re.M),r"\1"+ct['lowalert']+r"\2"+ct['default']+r"\3",CONT],
      [20,"","",re.compile(r"(\ +.*\ +)(connected)(\ +.*\ +.*)$",flags=re.M),r"\1"+ct['good']+r"\2"+ct['default']+r"\3",CONT],

      #interface configuration
      [20,"","",re.compile(BOL+r"(switchport mode )(.*)$",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],
      [20,"","",re.compile(BOL+r"(switchport trunk allowed vlan )(.*)$",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['default'],BREAK],

      #show ver
      [20,"","",re.compile(r"((?:\buptime|\brestarted|^Last reload).*)"),ct['general_value']+r"\1"+ct['default'],BREAK],
      [20,"","",re.compile(r"(\bSoftware.*)(Version [^, ]*\b)"),r"\1"+ct['important_value']+r"\2"+ct['default'],BREAK],
      [20,"","",re.compile(BOL+r"(\b(?:Configuration register|System image file) is )(.*)",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],

      #IOS router ping
      [20,"ping","",re.compile(BOS+r"[sS]ending [0-9]+",flags=re.M)], # only turns on ping effect
      #'.' and '!' means loss or received packets
      [20,"ping","ping",re.compile(r"^(\.\r?\n?)$",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],
      [20,"ping","ping",re.compile(r"(\!+[\r\n]?)$",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],

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

      # Reload confirmation
      [20,"","",re.compile(r"^(Proceed with reload\?)( \[confirm\].*)$",flags=re.M),ct['highalert']+r"\1"+ct['default']+r"\2",BREAK],

      # show log
      [20,"","",re.compile(r"(%.+-[0-3]-[0-9A-Z]+)(:)",flags=re.M),ct['alert']+r"\1"+ct['default']+r"\2",CONT],
      [20,"","",re.compile(r"(%.+-4-[0-9A-Z]+)(:)",flags=re.M),ct['lowalert']+r"\1"+ct['default']+r"\2",CONT],
      #[20,"","",re.compile(r"(%.+-[5-9]-[0-9A-Z]+)(:)",flags=re.M),ct['alert']+r"\1"+ct['default']+r"\2",CONT],

      # ASA show failover
      [20,"","",re.compile(BOL+r"(Last failover at )(.*)",flags=re.M),r"\1\2"+ct['general_value']+r"\3"+ct['default'],BREAK],
      [20,"","",re.compile(r"(?<=\): )(Normal \((?:Not-)?Monitored\))",flags=re.M),ct['good']+r"\1"+ct['default'],BREAK],
      [20,"","",re.compile(r"(?<=\): )(Normal )(\(Waiting\))",flags=re.M),ct['good']+r"\1"+ct['lowalert']+r"\2"+ct['default'],BREAK],
      [20,"","",re.compile(r"(?<=\): )(Failed(?: \(.*)?)",flags=re.M),ct['alert']+r"\1"+ct['default'],BREAK],

      # ASA show run access-list
      #  remark
      [20,"","",re.compile(BOL+r"(access-list [0-9a-zA-Z_-]+ )(remark .*)",flags=re.M),r"\1\2"+ct['comment']+r"\3"+ct['default'],BREAK],
      [20,"","",re.compile(BOL+r"(access-list\ [0-9a-zA-Z_-]+\ extended )(permit )((?:object-group\ [a-z0-9A-Z_-]+|[a-z]+)\ )(.*)",flags=re.M),r"\1\2"+ct['good']+r"\3"+ct['general_configitem']+r"\4"+ct['default']+r"\5",BREAK],
      [20,"","",re.compile(BOL+r"(access-list\ [0-9a-zA-Z_-]+\ extended )(deny )((?:object-group\ [a-z0-9A-Z_-]+|[a-z]+)\ )(.*)",flags=re.M),r"\1\2"+ct['alert']+r"\3"+ct['general_configitem']+r"\4"+ct['default']+r"\5",BREAK],

      # certmap tailing space
      [20,"","",re.compile(BOL+r"( subject-name co )(.* )$",flags=re.M),r"\1\2"+ct['highalert']+r"\3"+ct['default'],BREAK],
      # ISIS network ID
      #net 49.5001.1001.5914.9900.00
      [20,"","",re.compile(BOL+r"( net )([0-9]{2}\.(?:[0-9]{4}\.){4}[0-9]{2})$",flags=re.M),r"\1\2"+ct['important_value']+r"\3"+ct['default'],CLEAR],
      #VRF stuff
      [20,"","",re.compile(BOL+r"((?:ip route| ip| tunnel)? vrf(?: forwarding)? |ip vrf )([a-zA-Z0-9_-]+)( ?.*)$",flags=re.M),r"\1\2"+ct['important_value']+r"\3"+ct['default']+r'\4',CLEAR],


     ]
  return cmap
