import csv 
import os
import subprocess

outputFile = "torrentInfoData.csv"
inputFolder = "/Users/wpm/Desktop/analytics/info"
# data rows of csv file ( i <3 global variables )
rows = []  

def makeCSV():
    # field names - can add or remove later?
    fields = ['InfoHash', 'IP addresses and Ports', 'IP addresses', 'Number of IPs', 'Full geoIP dump', 'nslookup dump', 'whois dump'] 
    # name of csv file 
    filename = outputFile
    # writing to csv file 
    with open(filename, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)

def readData():
    i = 1
    allInfoHash = [] 
    for file in os.listdir(inputFolder):
        if file.endswith(".peers"):
            subRow = []
            fileString = str(file)
            infoHash = fileString.split("_", 1)[0]
            if infoHash not in allInfoHash:
                allInfoHash.append([infoHash])
                subRow.append(infoHash)
                subRow.append(ipAndPort(file))
                subRow.append(ip(file))
                subRow.append(len(subRow[-1]))
                subRow.append(geoIPfinder(ip(file)))
                subRow.append(nsLookupfinder(ip(file)))
                subRow.append(whoIS(ip(file)))
                rows.append(subRow)
                print(subRow)
                print(i)
                i = i + 1
    print(len(allInfoHash))

def ipAndPort(filename):
    data = []
    path = inputFolder + "/" + filename
    with open(path, 'r') as f:
        for line in f:
            if str(line).strip() not in data:
                data.append((str(line)).strip())
    return data

def ip(filename):
    data = []
    path = inputFolder + "/" + filename
    with open(path, 'r') as f:
        for line in f:
            if str(line).strip().split(":", 1)[0] not in data:
                data.append((str(line)).strip().split(":", 1)[0])
    return data

def geoIPfinder(ipList):
    data = []
    command = "mmdblookup -f /usr/local/var/GeoIP/GeoLite2-City.mmdb -i "
    for ip in ipList:
        output = str(subprocess.getoutput(command + ip))
        data.append(output)
    return data

def nsLookupfinder(ipList):
    data = []
    command = "nslookup "
    for ip in ipList:
        output = str(subprocess.getoutput(command + ip))
        data.append(output)
    return data

def whoIS(ipList):
    data = []
    command = "whois "
    for ip in ipList:
        try:
            output = str(subprocess.getoutput(command + ip))
            data.append(output)
        except:
            data.append("non utf8 output what the fuck why does whois do this")
    return data

def main():
    readData()
    makeCSV()

if __name__ == "__main__":
    main()
