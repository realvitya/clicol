#!/usr/bin/python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clicol import ct_dark,ct_light

for key, value in ct_dark.ct.iteritems():
    if key not in ct_light.ct:
        print "{0} item is not exists in light colortable".format(key)
        
for key, value in ct_light.ct.iteritems():
    if key not in ct_dark.ct:
        print "{0} item is not exists in dark colortable".format(key)
