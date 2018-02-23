#!/usr/bin/python
# Should be moved to test function as part of sanity check
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clicol import ct_dbg_net,ct_lbg_net

for key, value in ct_dbg_net.ct.iteritems():
    if key not in ct_lbg_net.ct:
        print "{0} item is not exists in light colortable".format(key)
        
for key, value in ct_lbg_net.ct.iteritems():
    if key not in ct_dbg_net.ct:
        print "{0} item is not exists in dark colortable".format(key)
"""
