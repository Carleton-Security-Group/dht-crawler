import sys
import bencodepy
import json

filename = sys.argv[1]
with open(filename) as file:
    unencodedData = file.read()
dictionaryData = json.loads(unencodedData)
bencodedData = bencodepy.encode(dictionaryData)


print("Raw data : ", unencodedData)
print("Dictionary data : ", dictionaryData)
print("Bencoded data : ", bencodedData)