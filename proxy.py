# TCP Proxy
# Allows users to analyze protocols, modify traffic being sent, and fuzzing

import sys
import socket
import threading

# Create HEX string; provide the character in the string if possible, otherwise place a period and move on
# Start with empty string and call join() with lambda fct
# if the length of the character is 3, we can print hex code for it, otherwise print '.'
# repr(): printable representation of an object (x is casted as a character) 
# HEX_FILTER = "".join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])

HEX_FILTER = "".join([chr(x) for x in range(256)])
