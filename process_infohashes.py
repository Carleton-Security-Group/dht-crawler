import os
import sys
import client
import datetime
import subprocess
import multiprocessing
import time

PEER_SEARCH_DEPTH = 5

INFO_DIR = 'info'


def handle_infohash(infohash):
    # Type of infohash should be string (40-byte hex representation of 20-byte integer)
    # Put infohash into databse
    client_id = client.get_random_20_bytes()
    peers = client.find_all_peers(infohash, client_id, PEER_SEARCH_DEPTH)
    # Put infohash-peer pairs into database with timestamp
    # TODO
    # Do something else with data?
    timestamp = datetime.datetime.isoformat(datetime.datetime.now())
    with open(f'{INFO_DIR}/{infohash}_{timestamp}.peers', 'w') as outfile:
        for ip, port in peers:
            outfile.write(f'{ip}:{port}\n')
    curl_args = ['curl', '-L', '--max-time', '10', '--output', f'{INFO_DIR}/{infohash}.torrent', f'http://itorrents.org/torrent/{infohash}.torrent']
    print(curl_args)
    subprocess.run(curl_args)
    with open(f'{infohash}.info', 'w') as info_file:
        subprocess.run(['transmission-show', f'{INFO_DIR}/{infohash}.torrent'], stdout=info_file)


os.makedirs(INFO_DIR)

for infile in sys.argv[1:]:
    with open(infile) as hashfile:
        for line in hashfile:
            proc = multiprocessing.Process(target=handle_infohash, args=(line.strip(),))
            proc.start()
            proc.join()
            proc.close()
