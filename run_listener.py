import sys
import os
import subprocess
import multiprocessing
import client
import time

ARCHLINUX = 'magnet:?xt=urn:btih:2f58e7d13e89abb76ed3eac491378cc17f7085eb&dn=archlinux-2022.02.01-x86_64.iso'
DEFAULT_PORT = 51413

NODE_COUNT = 10

RUNTIME = 60 * 60 * 24  # 24 hours

RESTART_EVERY = 60 * 15 # 15 minutes


def handle_infohash(infohash):
    # Put infohash into databse
    client_id = client.get_random_20_bytes()
    peers = client.find_all_peers(infohash, client_id)
    # Put infohash-peer pairs into database with timestamp
    #TODO
    # Do something else with data?
    # with open(f'{infohash}_{time.time()}.peers', 'w') as outfile:
    #     for ip, port in peers:
    #         outfile.write(f'{ip}:{port}\n')


def spawn_nodes_every(interval, start_port, count, start_time, runtime):
    while time.time() < start_time + runtime:
        for node in nodes:
            node.kill()
        nodes = []
        for port in range(start_port, start_port + count):
            #config_dir = f'/tmp/transmission_{port}'
            config_dir = f'/tmp/deluged_{port}'
            os.mkdir(config_dir)
            #args = ['transmission-cli', '-g', config_dir, '-p', str(port), ARCHLINUX]
            # Once archlinux is downloaded once, each node should just announce itself to the DHT
            args = ['deluged', '-c', config_dir, '-p', str(port)]
            node = subprocess.Popen(args, )
            nodes.append(node)
        start_port += count
        time.sleep(interval)
    for node in nodes:
        node.kill()


def main():
    if len(sys.argv) > 1:
        node_count = int(sys.argv[1])
    else:
        node_count = NODE_COUNT

    #tshark_args = ['tshark', '-i', '1', '-f', f'udp port {DEFAULT_PORT}-{DEFAULT_PORT+node_count}', '-d', f'udp.port=={DEFAULT_PORT}-{DEFAULT_PORT+node_count},bt-dht', '-O', 'bt-dht']
    tshark_args = ['tshark', '-O', 'bt-dht']

    tshark = subprocess.Popen(tshark_args, stdout=subprocess.PIPE)

    start_time = time.time()
    spawner = multiprocessing.Process(target=spawn_nodes_every, args=(RESTART_EVERY, DEFAULT_PORT, node_count, start_time, RUNTIME))
    spawner.start()

    children = []
    while time.time() < start_time + runtime:
        line = tshark.stdout.readline()
        line = line.decode("utf-8")
        line = line.strip()
        if (len(line) == 51) and (line[0:9] == "info_hash"):
            infohash = line[11:]
            sys.stdout.write(line + "\n")
            child = multiprocessing.Process(target=handle_infohash, args=(infohash,))
            child.start()
            children.append(child)
    for child in children:
        child.kill()
