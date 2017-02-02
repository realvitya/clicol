#!/usr/bin/python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clicol import colors

colors.print_colortable()
colors.print_allcolors()
