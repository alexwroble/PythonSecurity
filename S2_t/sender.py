# Author: Alexander Wroble
# See README for usage; use with requester.py and tracker.txt

import socket
import struct
import argparse
import math
import time
import datetime

print("starting sender...")

# prepare arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, help="the port on which the sender waits for requests", default="7777")
parser.add_argument("-g", "--reqPort", type=int, help="the port on which the requester is waiting", default="3333")
parser.add_argument("-r", "--rate", type=int, help="the number of packets to be sent per second", default="0")
parser.add_argument("-q", "--seq_no", type=int, help="the initial sequence of the packet exchange", default="1")
parser.add_argument("-l", "--length", type=int, help="the length of the payload (in bytes) in the packets", default="0")
args = parser.parse_args()

#PACKET TYPE (8 bit), SEQUENCE # (32-bit), LEN (32-bit), PAYLOAD (variable len)
# Packet layout
packetFormat = 'c I I 5120s' 

# print(args)

# STEP 1: WAIT FOR A REQUEST TO BE RECEIVED ------
myHostName = socket.gethostname() # get my name
myIP = socket.gethostbyname(myHostName) # get my ip
# print(socket.gethostbyname)
myPort = (myIP, args.port) # bind with this address to wait for mssg
sockIn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockIn.bind(myPort)
data, addr = sockIn.recvfrom(5132)
messageIn = struct.unpack(packetFormat, data)
payloadLen = messageIn[2]
# print("-Message In-")
# print(messageIn[0].decode('ascii')) # packet type
# print(messageIn[1]) # sequence number
# print(messageIn[2]) # length of payload
# print((messageIn[3])[:payloadLen].decode('ascii')) # payload
# print("-END Message In-")
sockIn.close()

# END STEP 1 -------------------------------------

# STEP 2: RETRIEVE REQUESTED INFORMATION ---------------
fileName = (messageIn[3])[:payloadLen].decode('ascii').strip()
with open(fileName, 'r') as reqFile:
    fileData = reqFile.read()
#     fileData = fileData.strip()

# with BytesIO(fileName) as reqFile:
#     fileData = reqFile.read()
# END STEP 2 -------------------------------------------

# STEP 3: SEND PAYLOAD REQUESTED BACK TO REQUESTER -----
# receiverAddr = ('127.0.0.1', args.reqPort)
receiverAddr = (addr[0], args.reqPort)
# Create a UDP socket
sockOut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# payloadVal = b"I received your request!"
# if the user specified a specific length, then we must divide the packet as requested
# cases 1: file data length is less than packet length -> send single packet, end packet
# case 2: file data length is greater than packet length -> send payload of size L until 
# remaining data to send is less than L, then send final packet and END packet
numPackets = 1 # default if user doesn't specify
maxBytesPerPack = args.length # either 5120 or args.length, whichever is smaller
if(args.length == 0):
    maxBytesPerPack = 5120

if(args.length != 0): # user argument supplied
    numPackets = math.ceil(len(fileData) / args.length)
elif (len(fileData) > 5120): # no -L supplied, but file doesn't fit in 1 packet
    numPackets = math.ceil(len(fileData) / 5120)

waitTime = 0 # in seconds
if(args.rate != 0):
    waitTime = 1/args.rate
# print(waitTime)
# [currIndex * maxBytesPerPack : (currIndex * maxBytesPerPack) + maxBytesPerPack]
binaryPayload = bytes(fileData, encoding='ascii')
currIndex = 0
sequenceNum = args.seq_no
# sequenceNumDumb = socket.htonl(sequenceNum)
for i in range(numPackets):
    # binaryPayload = bytes(fileData, encoding='ascii')
    startI = currIndex * maxBytesPerPack
    endI = startI + maxBytesPerPack
    if(i + 1 == numPackets):
        currPayload = binaryPayload[startI:]
    else:
        currPayload = binaryPayload[startI:endI]
    packetType = b'D'
    # data = (packetType, 123, len(payloadVal), payloadVal)
    data = (packetType, sequenceNum, len(currPayload), currPayload)
    packedData = struct.pack(packetFormat, *data)
    # Print stats right before sending
    print("DATA Packet")
    print("send time:       {}".format(datetime.datetime.now()))
    print("requester addr:  {}".format(receiverAddr[0]))
    print("Sequence num:    {}".format(sequenceNum))
    print("length:          {}".format(len(currPayload)))
    if(len(currPayload) < 4):
        print("payload:         {}".format(currPayload.decode('ascii')))
    else: 
        print("payload:         {}".format(currPayload[:4].decode('ascii')))
    print() # clean up terminal - add break in between data packet stats
    sockOut.sendto(packedData, receiverAddr)
    currIndex += 1
    sequenceNum += len(currPayload)
    if(waitTime != 0):
        time.sleep(waitTime)

# STEP 3B: send end packet
packetType = b'E' # END indicator
payload = b"END"
data = (packetType, sequenceNum, len(payload), payload)
# Print stats right before sending 
print("END Packet")
print("send time:       {}".format(datetime.datetime.now()))
print("requester addr:  {}".format(receiverAddr[0]))
print("Sequence num:    {}".format(sequenceNum))
print("length:          0")
print("payload:         ")
packedData = struct.pack(packetFormat, *data)

sockOut.sendto(packedData, receiverAddr)


sockOut.close() # close -> end of step 3

# END STEP 3 -----------------------------------------

# # Fields: Packet type, sequence number, length, payload
# packetType = b'D'
# # n_network = socket.htonl(n)
# sequence = 0x00000001
# s_network = socket.htonl(sequence)
# messg = b"hello"
# messgLen = len("hello")
# print("len(messg): %i" % len(messg))

# packageOut = struct.pack(packetFormat.format(19), packetType, sequence, len(messg), messg)
# format_string.format(len(payload_value)), char_value, net_num_value, int_value, payload_value

