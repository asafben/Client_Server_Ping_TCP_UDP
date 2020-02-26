"""
Author: Assaf Bentabou
Data: 24/02/20

Client-server python script for "ping" over TCP or UDP.
Utilities used for both client and server.
"""


def create_data_string(num_bytes):
    """
    Returns a an array of '1' bytes of size 'num_bytes'.
    :param num_bytes: Number of desired bytes, must be greater than 0.
    :type num_bytes int
    :return: num_bytes <=0 would return an empty binary string.
    :rtype: bytearray
    """
    if num_bytes <= 0:
        return b''
    return bytearray([1] * num_bytes)
