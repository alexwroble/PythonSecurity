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
        print("inside recv_from, no data received, break...")
        break
      buff += data
  except Exception as e:
    print("Error received in recv_from: {}".format(e))
    return buff
  print("returning without error from recv_from with buffer: {}".format(buff))
  return buff


# Modify request packs transporting through proxy prior to forwarding
def request_handler(buff):
  #TODO
  return buff


# Modify response packs transporting through proxy prior to forwarding
def response_handler(buff):
  #TODO
  return buff

# The cool proxy stuff! 
def proxy_handler(client_sock, remote_host, remote_port, receive_first):
  remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # establish conn to remote host (cont' below)
  remote_socket.connect((remote_host, remote_port)) # connect with supplied (IP, PORT) params
  print("Connected to remote socket HOST/PORT -- {}/{}".format(remote_host, remote_port))
  print("receive_first value: {}, type: {}".format(receive_first, type(receive_first)))
  # for some connection types, we may need to initiate connection to remote and req data before continuing. Check this here based on param
  if receive_first == True:
    remote_buff = recv_from(remote_socket) # receive data from remote socket, store in buffer
    hexdump(remote_buff) # get data from packet received, then continue

    remote_buff = response_handler(remote_buff) # pass in original remote buffer and update it with modified buffer returned from fct
    if len(remote_buff): # something exists in buffer... wait do I need this??? 
      client_sock.send(remote_buff)

  while True: 
    client_buff = recv_from(client_sock)
    # if we received something from client, print stats
    if len(client_buff):
      print(f"{len(client_buff)} bytes recceived from client")
      hexdump(client_buff)
      client_buff = request_handler(client_buff)
      remote_socket.send(client_buff)
      print("Data sent to remote")

  # after sending data, wait for response from remote host and call handler function for response received
    remote_buff = recv_from(remote_socket)
    # remote_buff = "test" # TESTING, REMOVE
    if len(remote_buff): # check if we've received anything before continuing
      print("{} bytes received from remote host".format(len(remote_buff)))
      hexdump(remote_buff) # print some stats
      # remote_buff = response_handler(remote_buff) # call handler to modify
      # .encode("utf-8")
      print("remote_buff: {}, type: {}".format(remote_buff, type(remote_buff)))
      client_sock.send(remote_buff.encode("utf-8"))
      print("Response sent to client")

    if not len(remote_buff) or not len(client_buff): # nothing more to do, exit loop
      client_sock.close()
      remote_socket.close()
      break
  return

# server connection management
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create server socket
  try:
    server.bind((local_host, local_port)) # bind: reserves port for use (cannot be used until conn is closed)
    # https://stackoverflow.com/questions/64145131/socket-bind-vs-socket-listen  // helpful for bind vs listen fcts for above
  except Exception as e: 
    print("Error binding server to remote HOST/PORT: {}".format(e))
    sys.exit()

  print("Server binded to Host/Port: {}/{}".format(local_host, local_port))
  server.listen(5) # See stack overflow link above; server listening for incoming packets; Max 5 conns
  while True:
    # accept method waits for incoming connection. When connection received, it returns a new socket obj of client and their address
    client_socket, addr = server.accept()
    print("Received connection from client address: {}".format(addr))
    # creating thread for comms between client and server:
    proxy_instance_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
    print("starting thread...")
    proxy_instance_thread.start()

def main():
  if len(sys.argv[1:]) != 5:
    print("Check arguments! Requires localhost, localport, remotehost, remoteport, receive_first")
    sys.exit(0)
  localhost = sys.argv[1]
  localport = int(sys.argv[2])
  remotehost = sys.argv[3]
  remoteport = int(sys.argv[4])
  receive_first = sys.argv[5]
  if receive_first.lower() == "true":
    receive_first = True
  else:
    receive_first = False

  server_loop(localhost, localport, remotehost, remoteport, receive_first)


if __name__ == "__main__":
  main()
