'''
import struct
import base64
def encode_timestamp(number):
    # number = 12314152151241
    if isinstance(number, float):
        number *= 100000
        number = int(number)
    number_bytes = number.to_bytes((number.bit_length() + 7) //8, byteorder="big")
    return base64.b62encode(number_bytes).decode()
    # b'CzMcqijJ'
'''

# Baishampayan Ghose
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _encode(num, alphabet):
    """Encode a positive number into Base X and return the string.

    Arguments:
    - `num`: The number to encode
    - `alphabet`: The alphabet to use for encoding
    """
    if num == 0:
        return alphabet[0]
    arr = []
    arr_append = arr.append  # Extract bound-method for faster access.
    _divmod = divmod  # Access to locals is faster.
    base = len(alphabet)
    while num:
        num, rem = _divmod(num, base)
        arr_append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def _decode(string, alphabet=BASE62):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for decoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

def encode_timestamp(number):
    # number = 12314152151241
    if isinstance(number, float):
        number *= 100000
        number = int(number)
    return _encode(number, alphabet=BASE62)

if __name__=='__main__':
    from datetime import datetime
    print(encode_timestamp(datetime.now().timestamp()))
    print(encode_timestamp(datetime.now().timestamp()))

