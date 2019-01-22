#[human_numbers]
#regex=(?<!MTU )(\d{1,3}(?=(?:\d{3})+(?!\d) (?:.*m)?(?:bytes|packets|pkts|bits|broadcasts|multicasts?|overrun|CRC|(?:in|out)put errors)))
#disabled=0
#replacement=\1,
#dependency=cisco_interface
#options=%(CONTINUE)s
#example=     853297735 packets input, 545445115336 bytes, 0 no buffer

from __future__ import print_function
from __future__ import unicode_literals
from builtins import input
import re

#import pudb

class HumanNumbers:
    loadonstart = True
    active = False

    def __init__(self):
        self.regex = re.compile(r"(?<!MTU )(\d{1,3}(?=(?:\d{3})+(?!\d) (?:.*m)?(?:bytes|packets|pkts|bits|broadcasts|multicasts?|overrun|CRC|unknown protocol|(?:in|out)put errors)))", re.M)

#    def preprocess(self, input = "", complete = True):
#        #.* is (?:up|.*down),
#        return input

    def postprocess(self, input = "", complete = True):
        return self.regex.sub(r"\1,", input)

