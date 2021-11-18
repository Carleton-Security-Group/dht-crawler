import socket
import sys
import bencodepy


ID = 'abcdefghij0123456789'
ID_BYTES = ID.encode('utf-8')
ID_INT = int.from_bytes(ID_BYTES, byteorder='big')

DEFAULT_SERVER = 'router.bittorrent.com'
DEFAULT_PORT = 6881


def get_random_20_bytes():
    return random.randint(0, 255**20)


def int_to_20_bytes(id_int):
    return id_int.to_bytes(length=20, byteorder='big')


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


def send_data_get_response(data_bytes, ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.sendto(data_bytes, (ip, port))
    data, address = s.recvfrom(4096)
    s.close()
    return data


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
    response = send_data_get_response(data_benc, server, port)
    resp_dict = bencodepy.decode(response)[b'r']
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
