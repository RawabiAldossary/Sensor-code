import socket
import auxutils

# Port and protocall for TCP Socket
udpSrcProtocol = 17
udpSrcPort = 1883
sock=socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))

# Loop for packets
while True:

    # Read packet header and compare
    pkt=sock.recvfrom(65565) #Capture packets from network
    pktProtocol = auxutils.ip_header(pkt[0][14:34])
    pktPort = auxutils.udp_header(pkt[0][34:42])

    if (pktProtocol['Protocol']==udpSrcProtocol) and (pktPort['Source Port']==udpSrcPort):
        print(pktPort['Length'])
        if (pktPort['Length']==1044):
            auxutils.writePkt1(pkt)
        if (pktPort['Length']==1038) :
            auxutils.writePkt2(pkt)
