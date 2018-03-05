# number_converter.py contains methods to convert a number to a short int / long-bit int string and back again

import struct


def encode_to_short(number):
    return struct.pack("<h", number)


def decode_to_short(byte_string):
    return struct.unpack("<h", byte_string)[0]


def encode_to_long(number):
    return struct.pack("<l", number)


def decode_to_long(byte_string):
    return struct.unpack("<l", byte_string)[0]
