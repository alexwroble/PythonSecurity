import socket
import argparse

def main(args):
    target_host = args.target_host
    target_port = args.target_port

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create sock obj

    client.connect((target_host, target_port)) # connect to server

    message = f"Well hello there!"
    client.sendall(message.encode("utf-8"))

    client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--target_host", type=str, help="target host", default='127.0.0.1')
    parser.add_argument('-p', "--target_port", type=int, help="target port", default=9998)
    args = parser.parse_args()   
    main(args)