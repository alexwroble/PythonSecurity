import socket
import threading

IP = '127.0.0.1'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket
    server.bind((IP, PORT)) # bind socket to address
    server.listen(5) # allow server to accept connections with param backlog of 5
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, addr = server.accept()
        print(f'[*] Accepted conn from {addr[0]}:{addr[1]}')
        c_handler = threading.Thread(target=handle_client, args=(client,))
        c_handler.start() #


def handle_client(client_socket):
    with client_socket as sock:
        req = sock.recv(1024)
        print(f'[*] Received: {req.decode("utf-8")}')


if __name__ == '__main__':
    main()