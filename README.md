# PythonSecurity

Author: Alexander Wroble

Creating this project based on my knowledge of course work at UW-Madison, self-studying and variety of textbooks to create a collection of network security tools and the ability to simulate them! :) 

Using netcat.py: 

  $ python netcat.py -t [127.0.0.1] -p [1234] -l -c  # Set up listener; this example uses IP addr localhost and a random port number of 1234
  
  ** In new terminal**
  
  $ python netcat.py -t [127.0.0.1] -p [1234]  # Running script in client-mode using same IP/PORT pair as above; You may need to click CTRL-D/CMD-D to send EOF as it waits for end-of-file marker when reading from stdin
  
  ** The command prompt will appear; example command below **
  >> cat /etc/passwd


Testing proxy.py locally: 

Terminal 1 -- 
>> python3 TCP_server.py -i 127.0.0.1 -p 9998   // Server listening on IP/PORT for incoming packs

Terminal 2 --
// localhost, localport, remotehost, remoteport, receive_first
>> python3 proxy.py 127.0.0.1 8080 127.0.0.1 9998 True  // binds to localhost/localport 

Terminal 3 -- 
>> python3 TCP_client.py -t 127.0.0.1 -p 8080

By running this, the client will send information to the proxy in which the proxy can modify the message (or simply pass it through), it then sends the (modified) response to the server