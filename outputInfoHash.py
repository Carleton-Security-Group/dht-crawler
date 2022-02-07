import subprocess
import sys
f = open("infohashes.txt", "a")
popenArgs = ['tshark', '-i', '1', '-f', 'udp port 51413', '-d', 'udp.port==51413,bt-dht', '-O', 'bt-dht']
proc = subprocess.Popen(popenArgs,stdout=subprocess.PIPE)
i = 1
while True:
    line = proc.stdout.readline()
    line = line.decode("utf-8") 
    line = line.strip()
    if (len(line) == 47) and (line[0:5] == "Value"):
        line = line[6:]
        sys.stdout.write(line + "\n")
        f.write(line + "\n")
        i = i + 1
        if (i % 100 == 0):
            f.flush()
