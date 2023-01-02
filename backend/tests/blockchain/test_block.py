from backend.blockchain.block import Block, GENESIS_DATA
import time
from backend.config import MINE_RATE, SECONDS
from backend.util.hex_to_binary import hex_to_binry
import pytest


def test_mine_block():
    last_block = Block.genesis()
    data = "test-data"

    block = Block.mine_block(last_block, data)

    assert isinstance(block, Block)
    assert block.data == data
    assert block.last_hash == last_block.hash
    assert hex_to_binry(block.hash)[0 : block.defficulty] == "0" * block.defficulty


def test_genesis():
    genesis = Block.genesis()

    assert isinstance(genesis, Block)
    for key, value in GENESIS_DATA.items():
        assert getattr(genesis, key) == value


def test_quickly_mined_block():
    last_block = Block.mine_block(Block.genesis(), "foo")
    mined_block = Block.mine_block(last_block, "bar")
    assert mined_block.defficulty == last_block.defficulty + 1


def test_slowly_mined_block():
    last_block = Block.mine_block(Block.genesis(), "foo")
    time.sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(last_block, "bar")

    assert mined_block.defficulty == last_block.defficulty - 1


def test_mine_block_defficulty_limits_at_1():
    last_block = Block(time.time_ns(), "test_last_hash", "test_hash", "test_data", 1, 0)
    time.sleep(MINE_RATE / SECONDS)
    mined_block = Block.mine_block(last_block, "bar")

    assert mined_block.defficulty == last_block.defficulty


@pytest.fixture
def last_block():
    return Block.genesis()


@pytest.fixture
def block(last_block):
    return Block.mine_block(last_block, "test-data")


def test_is_valid_block(last_block, block):
    Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_last_hash(last_block, block):
    block.last_hash = "evil_last_hash"
    with pytest.raises(Exception, match="The block last_hash must be correct"):
        Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_pro_of_work(last_block, block):
    block.hash = "fff"
    with pytest.raises(Exception, match="The proof of requirement was not met"):
        Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_defficulty(last_block, block):
    jumped_defficulty = 10
    block.defficulty = jumped_defficulty
    block.hash = f'{"0"*jumped_defficulty}1111abc'
    with pytest.raises(Exception, match="The block defficulty must only adjuest by 1"):
        Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_block_hash(last_block, block):
    block.hash = "000000000000bbab1111abc"
    with pytest.raises(Exception, match="Block hash must be correct"):
        Block.is_valid_block(last_block, block)
