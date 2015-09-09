from nose.tools import *
from bitcointech import basics
import io

POEM = [b"This little piggy went to market",
        b"This little piggy stayed at home",
        b"This little piggy had roast beef",
        b"This little piggy had none",
        b"And this little piggy went wee wee all the way home"]

def setup():
    print("SETUP!")

def teardown():
    print("TEAR DOWN!")

def test_commit_verify():
    msg = b"O Rose Thou Art Sick"

    com, key = basics.commit(msg)
    assert basics.verify(com, key, msg)

    assert not basics.verify(com, key, msg + b", The Invisible Worm")

def test_blockchain_add_block():
    f = io.BytesIO()
    blockchain = basics.BlockChain(f)
    for line in POEM:
        blockchain.add_block(line)

def test_blockchain_iterate():
    f = io.BytesIO()
    blockchain = basics.BlockChain(f)
    for line in POEM:
        blockchain.add_block(line)

    f.seek(0)
    data = f.read()

    g = io.BytesIO()
    g.write(data)
    blockchain = basics.BlockChain(g)

    for line, block in zip(reversed(POEM), blockchain):
        assert block.txndata.startswith(line), "Expected %s but was %s"%(line, block.txndata)
