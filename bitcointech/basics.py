"""

This module holds the cryptocurrency building blocks identified in the first week of lectures.

* commit
* verify
* HashPointer

"""
import hashlib
import struct
import Crypto.Random
import io
import os
import logging

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

def pad(data, header_len, boundary = 16):
    """ 
    pad the data out so it sits nicely on the 16 byte boundary, for 
    easier hexdump viewing
    """
    blocklen = len(data) + header_len
    p = boundary - (blocklen % boundary) - 1
    padding = struct.pack("!B%ds"%(p), p , b'\x00' * p) if p > 0 else b''
    return data + padding

class HashPointer:
    def __init__(self, ptr, hash = None, f = None, width = None):
        """ 
        initialise the hash pointer, either from ptr and hash, or from ptr
        and file f and width (HashPointer will initialise the hash)
        """
        self.ptr = ptr
        if hash:
            if f or width:
                raise ValueError("Either provide f and width or hash")
        else:
            if f == None or width == None:
                raise ValueError("Please provide f and width")
            if width == 0:
                hash = b'\x00' * 32
            else:
                f.seek(self.ptr)
                data = f.read(width)
                sha256 = hashlib.sha256()
                sha256.update(data)
                hash = sha256.digest()
        self.hash = hash

    def verify(self, f, width):
        f.seek(self.ptr)
        data = f.read(width)
        sha256 = hashlib.sha256()
        sha256.update(data)
        return sha256.digest() == self.hash

class Block:
    """
    Block structure:
    +------------------------------------------------------------------------+
    + 0xB10C | width(4) | prev(8) | prev_hash(32) | height(4) | txndata(var) +
    +------------------------------------------------------------------------+
            0x04      0x0C            0x2c    0x30          0x34
    prev: 
      offset of start of previous block (0 for the genesis block)
    prev_hash: 
      hash of the previous block (0 for genesis block)
    height:
      height of the block (0 for the genesis block)
    blocklen: 
      length of the transaction data segment (right padded to 16 byte boundary)
      padding is one byte length and zeros
    """

    MAGIC_BYTES = b'\xb1\x0c'
    HEADER_LEN = 2 + 4 + 8 + 32 + 4

    def __init__(self, prev_ptr, block_height, txndata):
        self.prev_ptr = prev_ptr
        self.block_height = block_height
        self.txndata = pad(txndata, self.HEADER_LEN)

    def pack(self):
        block = io.BytesIO()
        block.write(self.MAGIC_BYTES)
        block_len = self.HEADER_LEN + len(self.txndata)
        block.write(struct.pack("!IQ32sI", block_len, self.prev_ptr.ptr, 
            self.prev_ptr.hash, self.block_height))
        block.write(self.txndata)
        assert block.tell() % 16 == 0
        block.seek(0)
        return block.read() 

    @classmethod
    def unpack(Block, f, pos):
        f.seek(pos)
        magic = f.read(2)
        assert magic == b'\xb1\x0c'
        block_len, ptr, hash, block_height = struct.unpack("!IQ32sI", f.read(48))
        prev_ptr = HashPointer(ptr, hash = hash)
        txndata = f.read(block_len - Block.HEADER_LEN)
        return Block(prev_ptr, block_height, txndata)

def peek(f, w):
    pos = f.tell()
    d = f.read(w)
    f.seek(pos)
    return d

class BlockChain:

    def __init__(self, f):
        self.blockchain = f
        self.block_height = 0
        self.head = 0

        # advance to the end of an existing blockchain
        self.blockchain.seek(0)
        while peek(self.blockchain, 2) == Block.MAGIC_BYTES:
            pos = self.blockchain.tell()
            block = Block.unpack(self.blockchain, self.blockchain.tell())
            self.block_height += 1
            self.head = pos

    def add_block(self, txndata):
        """ add a block to the blockchain """
        if self.block_height == 0:
            # genesis block
            prev_ptr = HashPointer(self.head, f = self.blockchain, width = 0)
        else:
            self.blockchain.seek(self.head + 2)
            width = struct.unpack("!I", self.blockchain.read(4))[0]
            prev_ptr = HashPointer(self.head, f = self.blockchain, width = width)
        block = Block(prev_ptr, self.block_height, txndata)
        self.blockchain.seek(0, os.SEEK_END)
        new_head = self.blockchain.tell()
        self.blockchain.write(block.pack())
        self.block_height += 1
        self.head = new_head

    def __iter__(self):
        self.mark = self.head
        return self

    def __next__(self):
        if self.mark == -1:
            raise StopIteration
        block = Block.unpack(self.blockchain, self.mark)
        self.mark = block.prev_ptr.ptr if block.block_height > 0 else -1
        return block
