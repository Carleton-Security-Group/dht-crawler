import sys
import os
import subprocess
import multiprocessing
import client
import time

ARCHLINUX = 'magnet:?xt=urn:btih:2f58e7d13e89abb76ed3eac491378cc17f7085eb&dn=archlinux-2022.02.01-x86_64.iso'
DEFAULT_PORT = 51413

runtime = 60 * 60 * 24  # 24 hours


def handle_infohash(infohash):
    # Put infohash into databse
    client_id = client.get_random_20_bytes()
    client.find_all_peers(infohash, client_id)
    # Put infohash-peer pairs into database with timestamp


def main():
    if len(sys.argv) > 1:
        node_count = int(sys.argv[1])
    else:
        node_count = 5

    #tshark_args = ['tshark', '-i', '1', '-f', f'udp port {DEFAULT_PORT}-{DEFAULT_PORT+node_count}', '-d', f'udp.port=={DEFAULT_PORT}-{DEFAULT_PORT+node_count},bt-dht', '-O', 'bt-dht']
    tshark_args = ['tshark', '-O', 'bt-dht']

    tshark = subprocess.Popen(tshark_args, stdout=subprocess.PIPE)

    nodes = []
    for port in range(DEFAULT_PORT + 1, DEFAULT_PORT + node_count + 1):
        #config_dir = f'/tmp/transmission_{port}'
        config_dir = f'/tmp/deluged_{port}'
        os.mkdir(config_dir)
        #args = ['transmission-cli', '-g', config_dir, '-p', str(port), ARCHLINUX]
        # Once archlinux is downloaded once, each node should just announce itself to the DHT
        args = ['deluged', '-c', config_dir, '-p', str(port)]
        node = subprocess.Popen(args)
        nodes.append(node)

    children = []
    while True:
        line = tshark.stdout.readline()
        line = line.decode("utf-8")
        line = line.strip()
        if (len(line) == 51) and (line[0:9] == "info_hash"):
            infohash = line[11:]
            sys.stdout.write(line + "\n")
            #print(line)
            multiprocessing.Process(target=handle_infohash, args=(infohash,))
