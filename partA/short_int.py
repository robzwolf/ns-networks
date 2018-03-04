# short_int.py contains methods to convert a number to a short int string and back again


def encode(number):
    """
    Takes a number in the range 2^-15 to 2^15 - 1 and converts it to a two-character string.
    :param number:
    :return:
    """
    first_bit_string = bin(number)[2:][:-8]
    second_bit_string = bin(number)[2:][-8:]
    first_int = int(first_bit_string, base=2) if first_bit_string != "" else 0
    second_int = int(second_bit_string, base=2) if second_bit_string != "" else 0
    return chr(first_int) + chr(second_int)


def decode(string):
    """
    Takes a two-character string and converts it to a number in the range 2^-15 to 2^15 - 1.
    :param string:
    :return:
    """
    return (ord(string[0]) << 8) + ord(string[1])
