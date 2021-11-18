import socket
import sys
import bencodepy

#Contact Encoding
#Contact information for peers is encoded as a 6-byte string. Also known as "Compact IP-address/port info" the 4-byte IP address is in network byte order with the 2 byte port in network byte order concatenated onto the end.


if len(sys.argv) == 3:
    # Get "IP address of Server" and also the "port number" from argument 1 and argument 2
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    print("Run like : python3 client.py <arg1 server ip 192.168.1.102> <arg2 server port 4444 >")
    exit(1)

# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("Do Ctrl+c to exit the program !!")

# Let's send data through UDP protocol

send_data = "d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe"
#send_data = "d1:ad2:id20:abcdefghij01234567899:info_hash20:mnopqrstuvwxyz123456e1:q9:get_peers1:t2:aa1:y1:qe"
s.sendto(send_data.encode('utf-8'), (ip, port))
#s.sendto(send_data, (ip, port))
print("\n\n 1. Client Sent : ", send_data, "\n\n")
data, address = s.recvfrom(4096)
print("\n\n 2. Client received raw data : ", data, "\n\n")
#print("\n\n 2. Client received : ", data, "\n\n")
print("\n\n 2. Client received decoded : ", bencodepy.decode(data), "\n\n")


# close the socket
s.close()

