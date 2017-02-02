colors = {
          'default'  :r"\033[0m",
          'white'    :r"\033[37m",
          'u_white'  :r"\033[4;37m",
          'black'    :r"\033[30m",
          'u_black'  :r"\033[4;30m",

          'blue'     :r"\033[34m",
          'u_blue'   :r"\033[4;34m",
          'lblue'    :r"\033[94m",
          'u_lblue'  :r"\033[4;94m",
          'bblue'    :r"\033[38;5;21m",

          'green'    :r"\033[32m",
          'u_green'  :r"\033[4;32m",
          'lgreen'   :r"\033[92m",
          'u_lgreen' :r"\033[4;92m",
          'bgreen'   :r"\033[38;5;40m",

          'cyan'     :r"\033[36m",
          'u_cyan'   :r"\033[4;36m",
          'lcyan'    :r"\033[96m",
          'u_lcyan'  :r"\033[4;96m",
          'bcyan'    :r"\033[38;5;39m",

          'red'      :r"\033[31m",
          'u_red'    :r"\033[4;31m",
          'lred'     :r"\033[91m",
          'u_lred'   :r"\033[4;91m",
          'bred'     :r"\033[38;5;160m",

          'purple'   :r"\033[35m",
          'u_purple' :r"\033[4;35m",
          'lpurple'  :r"\033[95m",
          'u_lpurple':r"\033[4;95m",
          'bpurple'  :r"\033[38;5;165m",

          'brown'    :r"\033[38;5;94m",
          'lbrown'   :r"\033[38;5;130m",
           
          'yellow'   :r"\033[33m",
          'u_yellow' :r"\033[4;33m",
          'byellow'  :r"\033[93m",
          'u_byellow':r"\033[4;93m",

          'orange'   :r"\033[38;5;202m",

          'gray'     :r"\033[38;5;237m",
          'lgray'    :r"\033[37m",
          'u_lgray'  :r"\033[4;37m",
         }
def print_colortable():
   for text,color in colors.iteritems():
      print color.decode('string-escape')+text+" "+colors['default'].decode('string-escape'),
   print

def print_allcolors():
   print r"\33[XXm"
   for c in xrange(30,38):
      print "\033[%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(40,48):
      print "\033[%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(90,98):
      print "\033[%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(100,108):
      print "\033[%dm%d " % (c,c),
   print colors['default'].decode('string-escape')

   print
   print r"\33[4;XXm"
   for c in xrange(30,38):
      print "\033[4;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(40,48):
      print "\033[4;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(90,98):
      print "\033[4;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   for c in xrange(100,108):
      print "\033[4;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')

   print
   print r"\33[38;5;XXm"
   for c in xrange(256):
      print "\033[38;5;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')

   print
   print r"\33[48;5;XXm"
   for c in xrange(256):
      print "\033[48;5;%dm%d " % (c,c),
   print colors['default'].decode('string-escape')
   print
