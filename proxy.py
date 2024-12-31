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

# src: byte stream to be decoded, converted to text
# length: length of str displayed/translated per line (16 default/recommended)
# show: defaults to True; prints HEX/STR conversion
def hexdump(src, length=16, show=True):
  if isinstance(src, bytes): # check if src is a bytes object isinstance(obj, class)
    src = src.decode() # decode bytes obj

  results = [] # hex list
  for x in range(0, len(src), length):
    word = str(src[x:x+length])
    p_word = word.translate(HEX_FILTER) # Uses HEX_FILTER to map characters

    # ord(c) -- gets Unicode value of character 'c'
    # f'{ord(c):02X}' -- formats Unicode value as a two digit hex value: 
    #     02 makes it at least 2 chars wide for formatting, 'X' makes HEX val uppercase
    c_hex = ''.join([f'{ord(c):02X}' for c in word])
    width = length*3 # formatting
    # 04x -- ensures it is 4 digits wide and lowercase
    # :<{width} -- left aligned in character field of length "width"
    results.append(f'{x:04x}  {c_hex:<{width}}  {p_word}')
    if show:
      for line in results:
        print(line)
    else:
      return results
    
    
    
    
