import sys


def magnet_to_infohash(magnet):
    start = magnet.find('xt=urn:btih:') + 12
    if start != -1:
        return int(magnet[start:start + 40], base=16)
    return None


if __name__ == '__main__':
    print(magnet_to_infohash(sys.argv[1]))
