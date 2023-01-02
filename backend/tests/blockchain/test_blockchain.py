from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import GENESIS_DATA
import pytest
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet


def test_blockchain_instance():
    blockchain = Blockchain()
    assert blockchain.chain[0].hash == GENESIS_DATA.get("hash")


def test_add_block():
    blockchain = Blockchain()
    data = "test_data"
    blockchain.add_block(data)

    assert blockchain.chain[-1].data == data


@pytest.fixture
def blockchain():
    new_blockchain = Blockchain()
    for i in range(3):
        new_blockchain.add_block([Transaction(Wallet(), "recipt", i).serialize()])

    return new_blockchain


def test_is_valid_chain(blockchain):
    Blockchain.is_valid_chain(blockchain.chain)


def test_is_valid_chain_bad_genesis(blockchain):
    blockchain.chain[0].hash = "eveil_hash"
    with pytest.raises(Exception, match="The genesis block must be valid"):
        Blockchain.is_valid_chain(blockchain.chain)


def test_replace_chain(blockchain):
    blockchain_n = Blockchain()
    blockchain_n.replace_chain(blockchain.chain)

    assert blockchain_n.chain == blockchain.chain


def test_replace_chain_not_longer(blockchain):
    blockchain_n = Blockchain()
    with pytest.raises(
        Exception, match="Cannot replace, the incoming chain must be longer"
    ):
        blockchain.replace_chain(blockchain_n.chain)


def test_replace_chain_bad_chain(blockchain):
    blockchain_n = Blockchain()

    blockchain.chain[1].hash = "eveil fuck"
    with pytest.raises(Exception, match="The incoming chain is invalid"):
        blockchain_n.replace_chain(blockchain.chain)


def test_valid_transaction_chain(blockchain):
    Blockchain.is_valid_transaction_chain(blockchain.chain)


def test_is_valid_transaction_chain_duplicate(blockchain):
    transaction = Transaction(Wallet(), "recipt", 1).serialize()
    blockchain.add_block([transaction, transaction])

    with pytest.raises(Exception, match="is not unique"):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


def test_is_valid_transaction_chain_multiple_rewards(blockchain):
    reward_1 = Transaction.reward_transaction(Wallet()).serialize()
    reward_2 = Transaction.reward_transaction(Wallet()).serialize()

    blockchain.add_block([reward_1, reward_2])

    with pytest.raises(
        Exception, match="here can only be one mining reward per a block"
    ):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


def test_is_valid_transaction_chain_bad_transaction(blockchain):
    bad_transaction = Transaction(Wallet(), "recipt", 1)
    bad_transaction.input["signature"] = Wallet().sign(bad_transaction.output)
    blockchain.add_block([bad_transaction.serialize()])

    with pytest.raises(Exception):
        Blockchain.is_valid_transaction_chain(blockchain.chain)


def test_is_valid_trasnaction_chain_bad_historic_balance(blockchain):
    wallet = Wallet()
    bad_transaction = Transaction(wallet, "recip", 1)
    bad_transaction.output[wallet.address] = 9000
    bad_transaction.input["ammount"] = 9001
    bad_transaction.input["signature"] = wallet.sign(bad_transaction.output)
    blockchain.add_block([bad_transaction.serialize()])

    with pytest.raises(Exception, match="has invalid input amount"):
        Blockchain.is_valid_transaction_chain(blockchain.chain)
