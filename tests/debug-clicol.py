# 
import pkg_resources
import sys

if len(sys.argv) < 2:
    print("Please specify command to test! (test|file|cmd|telnet|ssh)")
    exit(1)
sys.argv[1] = 'clicol-'+sys.argv[1]
myscript = pkg_resources.load_entry_point('clicol', 'console_scripts', sys.argv[1])
args = None if len(sys.argv) < 2 else sys.argv[1:]
myscript(args)
