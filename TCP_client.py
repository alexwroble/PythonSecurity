import socket

target_host = '127.0.0.1'
target_port = 9998

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create sock obj

client.connect((target_host, target_port)) # connect to server

message = f"Well hello there"
client.sendall(message.encode("utf-8"))

client.close()