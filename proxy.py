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

# watch comms going through proxy; nodes at each end of proxy will connect via this
# conn: connection -- socket object
def recv_from(conn):
  buff = b''
  # timeout exception thrown when socket operation takes more than 5 seconds; for weak/long distance conns, increase; 5sec fine for localhost practice
  conn.settimeout(5) 
  try: 
    while True:
      data = conn.recv(4096)
      if not data:
        break
      buff += data
  except Exception as e:
    return buffer
  return buffer


# Modify request packs transporting through proxy prior to forwarding
def request_handler(buff):
  #TODO
  return buff


# Modify response packs transporting through proxy prior to forwarding
def response_handler(buff):
  #TODO
  return buff


def proxy_handler(client_sock, remote_host, remote_port, receive_first):
  remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # establish conn to remote host (cont' below)
  remote_socket.connect((remote_host, remote_port)) # connect with supplied (IP, PORT) params

  # for some connection types, we may need to initiate connection to remote and req data before continuing. Check this here based on param
  if receive_first:
    remote_buff = receive_from(remote_socket) # receive data from remote socket, store in buffer
    hexdump(remote_buff) # get data from packet received, then continue

  remote_buff = response_handler(remote_buff) # pass in original remote buffer and update it with modified buffer returned from fct
  if len(remote_buff): # something exists in buffer...
    client_socket.send(remote_buff)

  while True: 
    client_buff = receive_from(client_sock)
    # if we received something from client, print stats
    if len(client_buff):
      print(f"{len(client_buff)} bytes recceived from client")
      hexdump(client_buff)
      client_buff = request_handler(client_buff)
      remote_socket.send(client_buff)
      print("Data sent to remote")

  # after sending data, wait for response from remote host and call handler function for response received
    remote_buff = receive_from(remote_socket)
    if len(remote_buff): # check if we've received anything before continuing
      print("{} bytes received from remote host".format(len(remote_buff)))
      hexdump(remote_buff) # print some stats
      remote_buff = response_handler(remote_buff) # call handler to modify
      client_sock.send(remote_buff)
      print("Response sent to client")

    if not len(remote_buff) or not len(client_buff): # nothing more to do, exit loop
      client_sock.close()
      remote_socket.close()
      break
  return
      

  
  
    
    
