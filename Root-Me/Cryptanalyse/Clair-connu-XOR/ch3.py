#!/usr/bin/python3

FILENAME = "ch3.bmp"

KEY = b"fallen"

def read_file(filename:str) -> bytes:
    contents = ''''''
    with open(filename, "rb") as file:
        contents = file.read()
    return contents

def write_file(filename:str, contents:bytes):
    with open(filename, "wb") as file:
        file.write(contents)

def xor(data:bytes, key:bytes) -> bytes:
    result = b""
    for i in range(len(data)):
        result +=  int(data[i] ^ key[i % len(key)]).to_bytes(1, "little")
    return result


write_file("solve.bmp", xor(read_file(FILENAME), KEY))