# Author: Alexander Wroble

import os
import socket
import struct
import argparse
from collections import defaultdict
import datetime

# Made for primary use with sender.py
# UDP 
# Not identical purpose, but more advanced system than the TCP client/server system - maybe will upgrade later
#PACKET TYPE (8 bit), SEQUENCE # (32-bit), LEN (32-bit), PAYLOAD (variable len)
# PACKET TYPE OPTIONS: 
# 'R': REQ
# 'D': DATA
# 'E': END

# print("starting requester...")

# prepare command-line args
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, help="the port on which the requester waits for packets", default="3333")
parser.add_argument("-o", "--file_option", type=str, help="the name of the file that is being requested")
args = parser.parse_args()

packetFormat = 'c I I 5120s' # Packet format string to interpret/send packets

#Checking args
# print(args)
# print(args.file_option)

# STEP 1: OPEN AND READ TRACKER FILE ------------------------
trackerData = []
with open('tracker.txt', 'r') as trackerFile:
    for line in trackerFile:
        line = line.strip() # Remove end \n
        el = line.split() # separates elements of line by spaces and stores as list
        trackerData.append(el) # add el to list of requests from tracker.txt
        print(el) # TESTING

trackerDataSorted = sorted(trackerData, key=lambda x: x[1])
print("trackerDataSorted: ---------")
print(trackerDataSorted)
print("END trackerDataSorted: ---------")

grouped_dict = defaultdict(list)
for line in trackerDataSorted:
    grouped_dict[line[0]].append(line)

orderedSortedTracker = []
for key in grouped_dict:
    orderedSortedTracker.extend(grouped_dict[key])
# print("orderedSortedTracker: ---------")
# print(orderedSortedTracker)
# print("END orderedSortedTracker: ---------")
# print("Tracker Data: ")
# print(trackerData)
# uniqueFiles = []
# # for each line in tracker data, first get 
# for line in trackerData:
#     if line[0] not in uniqueFiles:
#         uniqueFiles.append(line[0])

# END STEP 1 ------------------------------------------------

# FOR EACH ROW OF tracker 
# for line in trackerData:
for line in orderedSortedTracker:
    # if(line[0] != "NONE")
    outputFileName = line[0]
    # if the user supplied a file name and the current line's file doesn't match, skip
    if(args.file_option != None and outputFileName != args.file_option):
        continue
    # at this point, line[0] is either the file specified by file_option or there was no specific file provided => proceed
    openMode = 'a' if os.path.exists(outputFileName) else 'w'
    

    # STEP 2: SEND REQUEST TO A SENDER --------------------------

    sockOut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sockOut.bind(('127.0.0.1', 7777)) # Eventually replace addr with (hostname, port num) from tracker.txt
    #sockOut.connect
    packetType = b'R' # Initial message is always a request to the sender
    packetSeq = 0
    #packetLen = len(trackerData[0][0])
    packetLen = len(line[0])
    # print(packetLen)
    # packetPayload = b"hello.txt"
    # packetPayload = bytes(trackerData[0][0], encoding='ascii')
    packetPayload = bytes(line[0], encoding='ascii')
    requestPacketData = (packetType, packetSeq, packetLen, packetPayload)
    packedReq = struct.pack(packetFormat, *requestPacketData)
    #sockOut.sendto(packedReq, ('127.0.0.1', 7777))
    #print(line[2]) # should be machine that it's on
    # senderAddr = (trackerData[0][2], int(trackerData[0][3]))
    senderIP = socket.gethostbyname(line[2]) # get IP of sender
    print("senderIP (socket.gethostbyname(line[2])): {}".format(senderIP))
    senderAddr = (senderIP, int(line[3]))
    print("sender addr: {}".format(senderAddr))

    sockOut.sendto(packedReq, senderAddr)
    sockOut.close()

    # END STEP 2 ------------------------------------------------

    # STEP 3: WAIT FOR RESPONSE FROM SENDER ---------------------
    # create socket "mySock"
    myHostName = socket.gethostname() # get my name
    print("myHostName: {}".format(myHostName))
    myIP = socket.gethostbyname(myHostName) # get my ip
    myIP = "127.0.0.1" # set as localhost for now instead of resolving to kali (127.0.1.1)
    sockIn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    myWaitingPortAddr = (myIP, args.port)
    print("myWaitingPortAddr: {}".format(myWaitingPortAddr))
    sockIn.bind(myWaitingPortAddr) # Bind to port from CLA

    myMessageTemp = bytes()
    FirstTimeRec = 0
    lastTimeRec = 0
    numDataPacks = 0
    numDataBytes = 0
    # startReceiving = datetime.datetime.now()
    timeDiff = -1
    while True:
        data, addr = sockIn.recvfrom(5132)
        recvTime = datetime.datetime.now()
        if(numDataPacks == 0): # first message
            FirstTimeRec = recvTime
        message = struct.unpack(packetFormat, data)
        payloadLen = message[2]
        if(message[0].decode('ascii') == 'E'):
            lastTimeRec = recvTime
            # Print End-packet stats
            print("End Packet")
            print("recv time:     {}".format(recvTime))
            print("sender addr:   {}:{}".format(addr[0], int(line[3])))
            print("sequence:      {}".format(message[1]))
            print("length:        0")
            print("payload:       0")
            print()
            # tempEnd = datetime.datetime.now()
            timeDiff = (recvTime - FirstTimeRec).total_seconds()
            break
        numDataPacks += 1
        numDataBytes += payloadLen
        # print data packet stats
        print("DATA Packet")
        print("recv time:     {}".format(recvTime))
        print("sender addr:   {}:{}".format(addr[0], int(line[3])))
        # sequenceDumb = socket.ntohl(message[1])
        print("sequence:      {}".format(message[1]))
        print("length:        {}".format(message[2]))
        tempMsg = message[3].decode('ascii')
        if(int(message[2]) < 4):
            print("payload:       {}".format(tempMsg))
        else:
            print("payload:       {}".format(tempMsg[:4]))
        print()

        myMessageTemp = myMessageTemp + (message[3])[:payloadLen]
    
    # transfer message to file:
    outputFile = open(outputFileName, openMode)
    outputFile.write((myMessageTemp.decode('ascii')))
    outputFile.close()

    # print sender stats
    print("Summary")
    print("sender addr:             {}:{}".format(senderAddr[0], senderAddr[1]))
    print("Total Data packets:      {}".format(numDataPacks))
    print("Total Data bytes:        {}".format(numDataBytes))
    packsPerSec = (numDataPacks + 1) / timeDiff
    print("Average packets/second:  {}".format(int(packsPerSec)))
    print("Duration of the test:    {} ms".format(int(timeDiff * 1000)))
    print()


        



    # print(myMessageTemp.decode('ascii'))

    # END STEP 3 ------------------------------------------------

    # while True:
    #     data, addr = mySock.recvfrom(1024) # buffer size is 1024 bytes
    #     #payloadLength = struct.unpack_from('I', data, 5)[0]
    #     buffer = bytes(5120)
    #     #updatedStructForm = packetFormat + str(payloadLength) + 's'
    #     #unloaded = struct.unpack(updatedStructForm, data)
    #     #payloadDecoded = unloaded[-1].decode('utf-8')
    #     print("payload decoded result: " + payloadDecoded)
    #     #packType, sequenceNum, payloadLen, payload = struct.unpack(packetFormat, data)
    #     # print("packType: %c, sequenceNum: %i, payloadLen: %i, payload: %s", packType, sequenceNum, payloadLen, payload)
    #     #print("received message: %s" % data)