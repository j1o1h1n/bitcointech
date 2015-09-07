"""

This module holds the cryptocurrency building blocks identified in the first week of lectures.

* commit
* verify
* HashPointer

"""
import hashlib
import struct
import Crypto.Random

def commit(msg):
    """
    The commit function takes a message as input and returns two values, a 
    commitment and a key
    """
    key = Crypto.Random.get_random_bytes(256 // 8)
    h = hashlib.sha256()
    h.update(key)
    h.update(msg)
    com = h.hexdigest()
    return (com, key)

def verify(com, key, msg):
    h = hashlib.sha256()
    h.update(key)
    h.update(msg)
    v = h.hexdigest()
    return com == v

class HashPointer:

    def __init__(self):
        pass
