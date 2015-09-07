from nose.tools import *
from bitcointech import basics
from bitcointech import goofycoin

def setup():
    print("SETUP!")

def teardown():
    print("TEAR DOWN!")

def test_basics():
    msg = b"O Rose Thou Art Sick"

    com, key = basics.commit(msg)
    assert basics.verify(com, key, msg)

    assert not basics.verify(com, key, msg + b", The Invisible Worm")

