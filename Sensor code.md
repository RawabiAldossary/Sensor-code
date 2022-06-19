# Sensore code

### Creating a docker file 


```python
FROM python:3.10
RUN apt-get update & apt-get upgrade 


WORKDIR /sever


COPY . .

ADD server2.py .


ADD requirments.txt .
ADD auxutils.py       .

RUN pip install  -r requirments.txt
CMD ["python" ,"./server2.py"]
```

 - python:3.10 is the base image  , 3.10 is the tage that I want 
for more python tage go to 




- WORKDIR /sever ==> is the directory of the python script




- Copy from my computer the CONTAINER /server dir



- ADD commands to files to my container 
     server.py is the name of my application 
     requirments.txt is the file the containes the dependencies required for running the code
     auxutils.py a custom library
     
     
     
- RUN  ==> for running the pip install command



- The CMD command specifies the instruction that is to be executed when a Docker container starts 
      python ==> The programming langauge 
      server ==> The name of python script 

     





## Running the docker file to build 


```python
docker build -t server_test
```

The docker build command builds Docker images from a Dockerfile and a “contex".


server_test ==> is the name of the image

## Mapping the container to port 1883


```python
docker run -p 1883:1883 server_test
```

Map the port 1883 in the container to port 1883 on the Docker host.

### The sensor code 


```python
import socket
import auxutils

udpSrcProtocol = 17
udpSrcPort = 1883
sock=socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))


while True:

    
    pkt=sock.recvfrom(65565) 
    pktProtocol = auxutils.ip_header(pkt[0][14:34])
    pktPort = auxutils.udp_header(pkt[0][34:42])

    if (pktProtocol['Protocol']==udpSrcProtocol) and (pktPort['Source Port']==udpSrcPort):
        print(pktPort['Length'])
        if (pktPort['Length']==1044):
            auxutils.writePkt1(pkt)
        if (pktPort['Length']==1038) :
            auxutils.writePkt2(pkt)
```

**Socket programming** is a way of connecting two nodes on a network to communicate with each other. One socket(node) listens on a particular port at an IP, while the other socket reaches out to the other to form a connection.

**sock.recvfrom(65565)** ==> Receive data from the socket. The return value is a pair (string, address) where string is a string representing the data received and address is the address of the socket sending the data

**auxutils.ip_header(pkt[0][14:34])** ==> upacking the ip header and storing the packet inofrmation is variables

**[0][14:43]** ==> Slice the array to exctract the ip header 

### Extracting the ip header 


```python
def ip_header(data):
    storeobj=struct.unpack("!BBHHHBBH4s4s", data)
    _version=storeobj[0]
    _tos=storeobj[1]
    _total_length =storeobj[2]
    _identification =storeobj[3]
    _fragment_Offset =storeobj[4]
    _ttl =storeobj[5]
    _protocol =storeobj[6]
    _header_checksum =storeobj[7]
    _source_address =socket.inet_ntoa(storeobj[8])
    _destination_address =socket.inet_ntoa(storeobj[9])

    data={'Version':_version,
    "Tos":_tos,
    "Total Length":_total_length,
    "Identification":_identification,
    "Fragment":_fragment_Offset,
    "TTL":_ttl,
    "Protocol":_protocol,
    "Header CheckSum":_header_checksum,
    "Source Address":_source_address,
    "Destination Address":_destination_address}
    return data
```

- **Struct**  The struct module in Python is used to convert native Python data types such as strings and numbers into a string of bytes and vice versa.



- **Pack** struct.pack() is the function that converts a given list of values into their corresponding string representation. It requires the user to specify the format and order of the values that need to be converted.



- **Upack** This function converts the strings of binary representations to their original form according to the specified format. The return type of struct.unpack() is always a tuple.



- **"!BBHHHBBH4s4s"** : 

  !	==> Big Endian	
  B	==> Integer	
  H	==>Integer	
  s	==> String	


```python

```
