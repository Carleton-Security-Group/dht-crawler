import socket
import sys
import bencodepy
import threading


ID = 'abcdefghij0123456789'
ID_BYTES = ID.encode('utf-8')
ID_INT = int.from_bytes(ID_BYTES, byteorder='big')

DEFAULT_SERVER = 'router.bittorrent.com'
DEFAULT_PORT = 6881

KNOWN_SERVERS = [
        ('router.bittorrent.com', 6881),
        ('router.utorrent.com', 6881),
        ('router.bitcomet.com', 6881),
        ('dht.transmissionbt.com', 6881),
        ('dht.aelitis.com', 6881),
        ]


def int_to_20_bytes(id_int):
    return id_int.to_bytes(length=20, byteorder='big')


def get_random_20_bytes():
    return int_to_20_bytes(random.randrange(0, 256**20))


def parse_id(id_bytes):
    if type(id_bytes) == type('string'):
        id_bytes = id_bytes.encode('utf-8')
    node_id = int.from_bytes(id_bytes, byteorder='big')
    return node_id


def parse_ip_port(ip_port_bytes):
    ip = list(ip_port_bytes)[:4]
    port = int.from_bytes(ip_port_bytes[4:], byteorder='big')
    return ip, port


def parse_node_info(node_info_bytes):
    node_id = parse_id(node_info_bytes[:20])
    ip, port = parse_ip_port(node_info_bytes[20:])
    return node_id, ip, port


def parse_nodes_info_block(node_info_bytes):
    if len(node_info_bytes) % 26 != 0:
        print('WARNING: attempting to parse block of compact node infos but block size % 26 != 0', file=sys.stderr)
    node_infos = []
    for i in range(len(node_info_bytes) // 26):
        node_id, ip, port = parse_node_info(node_info_bytes[i*26:(i+1)*26])
        node_infos.append({'id': node_id, 'ip': ip, 'port': port})
    return node_infos


def send_data_get_response(data_bytes, ip, port, data=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    try:
        s.sendto(data_bytes, (ip, port))
    except socket.gaierror:
        print(f'ERROR: getaddrinfo error trying to send to {ip}:{port}', file=sys.stderr)
        return None
    resp_data, address = s.recvfrom(4096)
    s.close()
    if data is not None:
        data.append(resp_data)
    else:
        return resp_data


def send_data_get_response_with_timeout(data_bytes, ip, port, timeout):
    if type(ip) == type([]):
        ip = '.'.join([str(num) for num in ip])
    data = []
    thread = threading.Thread(
            target=send_data_get_response,
            args=(data_bytes, ip, port),
            kwargs={'data': data},
            daemon=True,
            )
    thread.start()
    thread.join(timeout=timeout)
    assert len(data) < 2
    if len(data) == 1:
        return data[0]
    return None


def ping(server, port, client_id=ID):
    '''
    Pings the given server on the given port, sending client_id as the querying
    client id (defaults to abcdefghij0123456789).

    Response should contain the node id of the responding server.

    Returns response in dict format.
    '''
    if type(client_id) == type(1234):
        client_id = int_to_20_bytes(client_id)
    data_dict = {
            't': 'aa',
            'y': 'q',
            'q': 'ping',
            'a': {'id': client_id}
            }
    data_benc = bencodepy.encode(data_dict)
    response = send_data_get_response(data_benc, server, port)
    resp_dict = bencodepy.decode(response)[b'r']
    output = {'id': parse_id(resp_dict[b'id'])}
    return output


def find_node(target, server, port, client_id=ID):
    '''
    Queries the given server on the given port for the contact information for
    the node id given by target.
    The contact information takes the form of a compact node info bytestring,
    where the first 20 bytes are the node id, and the remaining 6 bytes are
    the IP address and port of that node.

    The response contains the node id of the queried server and the contact
    information for the target node.
    If the target node is not found, the response instead has a list of the
    contact information for the k (usually 16) nodes with ids which most closely
    match the target.

    Returns response in dict format.
    '''
    if type(target) == type(1234):
        target = int_to_20_bytes(target)
    if type(client_id) == type(1234):
        client_id = int_to_20_bytes(client_id)
    data_dict = {
            't': 'aa',
            'y': 'q',
            'q': 'find_node',
            'a': {'id': client_id, 'target': target}
            }
    data_benc = bencodepy.encode(data_dict)
    response = send_data_get_response(data_benc, server, port)
    resp_dict = bencodepy.decode(response)[b'r']
    output = {
            'id': parse_id(resp_dict[b'id']),
            'nodes': parse_nodes_info_block(resp_dict[b'nodes'])
            }
    return output


def get_peers(info_hash, server, port, client_id=ID):
    '''
    Queries the given server on the given port for peers associated with the
    given info hash.

    The response is the node id of the queried server, a token which will be
    necessary if the client wishes to announce_peer for the info hash in the
    future, and either 'values' or 'nodes'.
    If the response contains 'values', then the associated value is a list of
    IP/port tuples for peers associated with the given info hash.
    If the response contains 'nodes', then there are no peers associated with
    the given info hash, and instead the value for 'nodes' is the k (usually 16)
    nodes in the queried node's routing table closest to the given info_hash.

    Returns response in dict format.
    '''
    if type(info_hash) == type(1234):
        info_hash = int_to_20_bytes(info_hash)
    if type(client_id) == type(1234):
        client_id = int_to_20_bytes(client_id)
    data_dict = {
            't': 'aa',
            'y': 'q',
            'q': 'get_peers',
            'a': {'id': client_id, 'info_hash': info_hash}
            }
    data_benc = bencodepy.encode(data_dict)
    response = send_data_get_response_with_timeout(data_benc, server, port, 5.0)
    if response is None:
        return None
    try:
        data_dict = bencodepy.decode(response)
    except bencodepy.exceptions.DecodingError:
        print('ERROR: get_peers() cannot bdecode response:', file=sys.stderr)
        return None
    if b'r' not in data_dict:
        print('ERROR: get_peers() bencoded dict missing \'r\' key:', file=sys.stderr)
        return None
    resp_dict = data_dict[b'r']
    output = {'id': parse_id(resp_dict[b'id'])}
    if b'token' in resp_dict:
        output['token'] = resp_dict[b'token']
    if b'values' in resp_dict:
        output['values'] = [parse_ip_port(peer) for peer in resp_dict[b'values']]
        if b'token' not in resp_dict:
            print('WARNING: get_peers() returned list of ips but didn\'t return a token', file=sys.stderr)
    if b'nodes' in resp_dict:
        output['nodes'] = parse_nodes_info_block(resp_dict[b'nodes'])
    return output


def find_nodes_from_server(info_hash, server, port, client_id=ID, values=None, lock=None, depth=5):
    if depth <= 0:
        return []
    response = get_peers(info_hash, server, port, client_id)
    if response == None:
        return []
    if 'values' in response:
        if values is not None:
            lock.acquire()
            values.extend(response['values'])
            lock.release()
        else:
            return response['values']
    elif 'nodes' in response:
        child_values = []
        child_lock = threading.Lock()
        children = []
        for node in response['nodes']:
            child = threading.Thread(
                    target=find_nodes_from_server,
                    args=(info_hash, node['ip'], node['port'], client_id),
                    kwargs={'values': child_values, 'lock': child_lock, 'depth': depth-1})
            children.append(child)
            child.start()
        for child in children:
            child.join()
        if values is not None:
            lock.acquire()
            values.extend(child_values)
            lock.release()
        else:
            return child_values


def find_all_peers(info_hash, client_id=ID):
    values = []
    for server, port in KNOWN_SERVERS:
        values += find_nodes_from_server(info_hash, server, port, client_id)
    return values


def announce_peer(info_hash, listen_port, token, server, port, client_id=ID):
    '''
    Announces to the given server on the given port that the client is
    downloading the file associated with the given info hash on the port given
    by listen_port.
    The given token is a token which was received in response to a previous
    get_peers query for the given info hash.
    The server then store the IP address and listen_port of the client under
    the given info hash in its store of peer contact information.

    Could be useful to announce_peer on a port and then listen as connections
    come in for peers looking to torrent the file with the given info hash.

    The response is the node id of the queried server.

    Returns response in dict format.
    '''
    if type(info_hash) == type(1234):
        info_hash = int_to_20_bytes(info_hash)
    if type(client_id) == type(1234):
        client_id = int_to_20_bytes(client_id)
    data_dict = {
            't': 'aa',
            'y': 'q',
            'q': 'announce_peer',
            'a': {
                'id': client_id,
                'implied_port': 0,  # optional. If nonzero, ignore port arg and use UDP source port instead
                'info_hash': info_hash,
                'port': listen_port,
                'token': token
                }
            }
    data_benc = bencodepy.encode(data_dict)
    response = send_data_get_response(data_benc, server, port)
    resp_dict = bencodepy.decode(response)[b'r']
    output = {'id': parse_id(resp_dict[b'id'])}
    return output


def parse_args():
    if len(sys.argv) == 3:
        return sys.argv[1], int(sys.argv[2])
    elif len(sys.argv) == 1:
        return DEFAULT_SERVER, DEFAULT_PORT
    else:
        print(f'Usage: python3 {sys.argv[0]} [SERVER] [PORT]', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    import random
    import pprint

    server, port = parse_args()

    # client_id = get_random_20_bytes()
    client_id = ID

    ping_dict = ping(server, port, client_id)
    print(f'\nResponse from ping(server={server}, port={port}, client_id={client_id}):')
    pprint.pprint(ping_dict, indent=2)

    target_node = get_random_20_bytes()
    find_node_dict = find_node(target_node, server, port, client_id)
    print(f'\nResponse from find_node(target={target_node}, server={server}, port={port}, client_id={client_id}):')
    pprint.pprint(find_node_dict, indent=2)

    info_hash = get_random_20_bytes()
    get_peers_dict = get_peers(info_hash, server, port, client_id)
    print(f'\nResponse from get_peers(info_hash={info_hash}, server={server}, port={port}, client_id={client_id}):')
    pprint.pprint(get_peers_dict, indent=2)

    if False:   # if you want to chance your IP appearing in a DHT
        listen_port = 1234
        announce_peer_dict = announce_peer(info_hash, listen_port, get_peers_dict['token'], server, port, client_id)
        print(f'\nResponse from announce_peer(info_hash={info_hash}, listen_port={listen_port}, token={get_peers_dict["token"]}, server={server}, port={port}, client_id={client_id}):')
        pprint.pprint(announce_peer_dict, indent=2)

    from magnet_to_infohash import magnet_to_infohash
    archlinux_magnet = 'magnet:?xt=urn:btih:2f58e7d13e89abb76ed3eac491378cc17f7085eb&dn=archlinux-2022.02.01-x86_64.iso'
    info_hash = magnet_to_infohash(archlinux_magnet)
    print(f'\nGetting peers for {archlinux_magnet} ...')
    peers = find_all_peers(info_hash, client_id)
    pprint.pprint(peers, indent=2)
