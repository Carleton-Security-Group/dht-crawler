import sys


def infohash_to_magnet(info_hash):
    return f'magnet:?xt=urn:btih:{info_hash:x}'


if __name__ == '__main__':
    print(infohash_to_magnet(sys.argv[1]))
