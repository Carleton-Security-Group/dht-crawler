# A ping query has a single argument, "id" the value is a 20-byte string containing the senders node ID in network byte order. 
# The appropriate response to a ping has a single key "id" containing the node ID of the responding node.
# ping Query = {"t":"aa", "y":"q", "q":"ping", "a":{"id":"abcdefghij0123456789"}}
# bencoded = d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe
# Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
# bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
import sys
import bencodepy
from random import randrange

filename = sys.argv[1]
with open(filename) as file:
    # user supplies node ID
    nodeID = file.read()
#randomly generate a transaction ID 
transactionID = hex(randrange(256))
transactionID = transactionID[2:]

dhtPing = {"t":transactionID, "y":"q", "q":"ping", "a":{"id":nodeID}}
bencodedPing = bencodepy.encode(dhtPing)

print("Raw ping : ", dhtPing)
print("Bencoded ping : ", bencodedPing)