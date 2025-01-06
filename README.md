# PythonSecurity

Author: Alexander Wroble

Creating this project based on my knowledge of course work at UW-Madison, self-studying and variety of textbooks to create a collection of network security tools and the ability to simulate them! :) 

Using netcat.py: 

  $ python netcat.py -t [127.0.0.1] -p [1234] -l -c  # Set up listener; this example uses IP addr localhost and a random port number of 1234
  
  ** In new terminal**
  
  $ python netcat.py -t [127.0.0.1] -p [1234]  # Running script in client-mode using same IP/PORT pair as above; You may need to click CTRL-D/CMD-D to send EOF as it waits for end-of-file marker when reading from stdin
  
  ** The command prompt will appear; example command below **
  > cat /etc/passwd


Testing proxy.py locally: 

>Terminal 1 -- 
>> python3 TCP_server.py -i 127.0.0.1 -p 9998   // Server listening on IP/PORT for incoming packs

>Terminal 2 --
>localhost, localport, remotehost, remoteport, receive_first
>> python3 proxy.py 127.0.0.1 8080 127.0.0.1 9998 True  // binds to localhost/localport 

>Terminal 3 -- 
>> python3 TCP_client.py -t 127.0.0.1 -p 8080

>By running this, the client will send information to the proxy in which the proxy can modify the message (or simply pass it through), it then sends the (modified) response to the server


Distributed File Transfer System: (network sim, spicy attacks to come later)
> requester.py
> sender.py
> tracker.txt
>> Format: file_name sequence_number sender_hostname sender_port

>> values separated by single space; example -- 

>>> myFile.txt 1 127.0.0.1 5500

>>> myFile.txt 3 127.0.0.1 5600

>>> myFile.txt 2 127.0.0.1 6500

>> rmk: the sequence number doesn't need to be in any specific order, the requester will sort and reach out to the senders in order regardless

> Packet layout [9 byte header, variable length payload]: 
>> packet type: 8 bits (1 byte)
>> sequence number (can be arbitrary for sender -- internal use only; increments automaticaly by bytes in the payload added): 32 bits (4 bytes)
>> length (bytes in payload; '0' for request packets): 32 bits (4 bytes)

> Attack ideas: DoS, Eavesdropping, file poisoning


Basic requester/sender testing: 

> requester.py usage: 

>> -p --port: Port that requester waits for incoming packets
>> -0 --file_option: name of file being requested

> sender.py usage: 

>> -p --port: Port that the sender waits for incoming request packets
>> -g --reqPort: port that the requester is waiting
>> -r --rate: number of packets to be sent per second (choose a higher value for freaky-fast delivery ;)
>> -q --seq_no: inital sequence of the packet exchange
>> -l --length: length of the payload (in bytes)



>> Place the requester.py file in one folder, and each sender in its own folder below root

>> Place the tracker.txt document in the requester's folder, and the piece of the files in the corresponding sender's folder
>> tracker.txt: 
>>> testFile.txt 1 localhost 6767

>> In terminal 1, activate sender1: python3 sender.py -p 6767 -g 5454 -r 100 -q 100 -l 50

>> In terminal 2, activate requester: python3 requester.py -p 5454 -o testFile.txt

>> RMK: The current sender.py in S1_t contains additional print statements for testing/debugging; also has hostname hard coded for localhost (had problems testing with use of kali VM and MacOS when resolving host IP address)