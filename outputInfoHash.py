import subprocess
import sys
popenArgs = ['tshark', '-i', '1', '-f', 'udp port 51413', '-d', 'udp.port==51413,bt-dht', '-O', 'bt-dht']
proc = subprocess.Popen(popenArgs,stdout=subprocess.PIPE)
while True:
    line = proc.stdout.readline()
    line = line.decode("utf-8") 
    line = line.strip()
    if (len(line) == 51) and (line[0:9] == "info_hash"):
        line = line[11:]
        sys.stdout.write(line + "\n")
        #print(line)