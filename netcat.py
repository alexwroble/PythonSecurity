# netcat can be used to read and write data across a network, including spawning
# shells and executing commands. Since it is usually removed, I'll try to create st
# similar (emphasis on "try")

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# Receives a command, runs, and returns output as string
def execute(cmd):
    # ensure a command actually exists, prep
    cmd = cmd.strip()
    if not cmd:
        return
    
    # check_output: runs command on local OS and returns output
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    # Init NetCat obj with args from CL, then create socket obj
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # either listening or sending based on args from user
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        # connect to target and port, send buffer if one exists
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            # wait to receive data from target; continues until user ends session
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    # break if no more data
                    if recv_len < 4096:
                        break
                    if response:
                        print(response)
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print("Terminated")
            self.socket.close()
            sys.exit() # cash tf out

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            # pass conn to handle fct 
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # needs testing
    def handle(self, client_socket):
        # if execute cmd exists, call execute fct with cmd supplied in CL args
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode()) # Send output back on socket
        elif self.args.upload: # Upload arg exists; used when in listening mode, receives file on connected IP/PORT
            f_buff = b'' # binary stream for file data
            while True:
                data_rec = client_socket.recv(4096)
                if data_rec:
                    f_buff += data_rec
                else:
                    break
            # After receiving data to upload to file, create/open file name from args and write buffer to file; 
            # Sends confirmation to client socket as response
            with open(self.args.upload, "wb") as myFile: 
                myFile.write(f_buff)
                response = f'Saved File: {self.args.upload}'
                client_socket.send(response.encode())
        elif self.args.command:
            




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BHP Net Tool", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     epilog=textwrap.dedent("""
Examples:
    netcat.py -t 127.0.0.1 -p 5555 -l -c # Command Shell
    netcat.py -t 127.0.0.1 -p 5555 -l -u=something.txt # upload to file
    netcat.py -t 127.0.0.1 -p 5555 -l -e=\"cat /etc/passwd\" # execute cmd
    echo "Hi" | ./netcat.py -t 127.0.0.1 -p 123 # echo text to server port 123
    netcat.py -t 127.0.0.1 -p 5555 # connect to server 
"""))
    parser.add_argument('-c', "--command", action="store_true", help="command shell")
    parser.add_argument('-e', "--execute", help="execute command")
    parser.add_argument('-l', "--listen", action="store_true", help="listen")
    parser.add_argument('-p', "--port", type=int, default=5555, help='specify port')
    parser.add_argument('-t', "--target", default="127.0.0.1", help="specified IP")
    parser.add_argument('-u', "--upload", help="upload file")
    args = parser.parse_args()
    if args.listen:
        buffer = ""
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()
