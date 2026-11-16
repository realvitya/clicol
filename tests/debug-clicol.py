# 
import sys
from clicol._compat import metadata

if len(sys.argv) < 2:
    print("Please specify command to test! (test|file|cmd|telnet|ssh)")
    exit(1)
sys.argv[1] = 'clicol-'+sys.argv[1]
myscript = next(entrypoint for entrypoint in metadata.distribution('clicol').entry_points
                if entrypoint.group == 'console_scripts' and entrypoint.name == sys.argv[1]).load()
args = None if len(sys.argv) < 2 else sys.argv[1:]
myscript(args)
