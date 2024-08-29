#!/usr/bin/python3
import hashlib
import base64
import re
import gzip
import random
import sys

def _get_seed_from_plaintext_file(file):
    text = file.read()
    match_str = re.search('seed=.* ref', text).group()
    begin_pos = match_str.find(',') + 1
    end_pos = match_str.rfind('"')
    return match_str[begin_pos:end_pos]

def get_seed_from_file(filename):
    GZIP_MAGIC_NUMBER = b'\x1f\x8b'
    f = open(filename, 'rb')
    if f.read(2) == GZIP_MAGIC_NUMBER:
        f.close()
        f = gzip.open(filename, 'rt')
    else:
        f.close()
        f = open(filename, 'r')
    return _get_seed_from_plaintext_file(f)

def seed_to_array(seed_str):
    seed_bytes = base64.b64decode(seed_str)
    result = []
    for i in range(len(seed_bytes) // 4):
        result.append(int.from_bytes(seed_bytes[i*4:i*4+4], byteorder='little'))
    return result

N = 624
mt = [0] * N
mti = N + 1
def init_genrand(s):
    global mt
    global mti
    mt[0] = s & 0xffffffff
    mti = 1
    while mti < N:
        mt[mti] = (1812433253 * (mt[mti-1] ^ (mt[mti-1] >> 30)) + mti)
        mt[mti] &= 0xffffffff
        mti += 1

def init_by_array(init_key, key_length):
    global mt
    init_genrand(19650218)
    i = 1
    j = 0
    k = (N if N > key_length else key_length)
    while k != 0:
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525)) + init_key[j] + j # non linear
        mt[i] &= 0xffffffff
        i += 1
        j += 1
        if i >= N:
            mt[0] = mt[N-1]
            i = 1
        if j >= key_length:
            j = 0
        k -= 1
    k = N - 1
    while k != 0:
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941)) - i # non linear
        mt[i] &= 0xffffffff
        i += 1
        if i>=N:
            mt[0] = mt[N-1]
            i = 1
        k -= 1
    mt[0] = 0x80000000

haiDisp = ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]

def gen_yama_from_seed(seed_str):
    seed_array = seed_to_array(seed_str)
    init_by_array(seed_array, 2496/4)
    #print(mt[623])
    mt_state = tuple(mt + [624])
    random.setstate((3, mt_state, None))
    for nKyoku in range(10):
        rnd = [0] * 144
        rnd_bytes = b''
        src = [random.getrandbits(32) for _ in range(288)]
        #print(src[0])
        for i in range(9):
            hash_source = b''
            for j in range(32):
                hash_source += src[i*32+j].to_bytes(4, byteorder='little')
            rnd_bytes += hashlib.sha512(hash_source).digest()
        for i in range(144):
            rnd[i] = int.from_bytes(rnd_bytes[i*4:i*4+4], byteorder='little')
        # till here, rnd[] has been generated
        yama = [i for i in range(136)]
        for i in range(136 - 1):
            temp = yama[i]
            yama[i] = yama[i + (rnd[i]%(136-i))]
            yama[i + (rnd[i]%(136-i))] = temp
        # print('nKyoku=' + str(nKyoku) + ' yama=')
        for i in range(135, -1, -1):
            print(haiDisp[yama[i] // 4], end='')
        print('')

def test_mt_init():
    init_genrand(19650218)
    mt_state = tuple(mt + [624])
    random.setstate((3, mt_state, None))
    print(random.getrandbits(32))


if __name__ == "__main__":
    #test_mt_init()
    filename = sys.argv[1]
    seed_str = get_seed_from_file(filename)
    gen_yama_from_seed(seed_str)

