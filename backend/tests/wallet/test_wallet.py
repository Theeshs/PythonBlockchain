from backend.config import STARTING_BALANCE
from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain
from backend.wallet.transaction import Transaction
import pytest
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


def test_verify_valid_signature():
    data = {"foo": "test_data"}
    wallet = Wallet()
    signaure = wallet.sign(data)

    assert Wallet.verify(wallet.public_key, data, signaure)


def test_verify_invalid_sinature():
    data = {"foo": "test_data"}
    wallet = Wallet()
    signaure = wallet.sign(data)

    assert not Wallet.verify(Wallet().public_key, data, signaure)


def test_calculate_balance():
    blockchain = Blockchain()
    wallet = Wallet()

    assert wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE

    ammount = 50

    transaction = Transaction(wallet, "recip", ammount)
    blockchain.add_block([transaction.serialize()])

    assert (
        wallet.calculate_balance(blockchain, wallet.address)
        == STARTING_BALANCE - ammount
    )

    recieved_ammout_1 = 25
    recieved_transaction_1 = Transaction(Wallet(), wallet.address, recieved_ammout_1)

    recieved_ammout_2 = 45
    recieved_transaction_2 = Transaction(Wallet(), wallet.address, recieved_ammout_2)
    blockchain.add_block(
        [recieved_transaction_1.serialize(), recieved_transaction_2.serialize()]
    )

    assert (
        wallet.calculate_balance(blockchain, wallet.address)
        == STARTING_BALANCE - ammount + recieved_ammout_1 + recieved_ammout_2
    )


def test_reward_transaction():
    miner_wallet = Wallet()
    transaction = Transaction.reward_transaction(miner_wallet)

    assert transaction.input == MINING_REWARD_INPUT
    assert transaction.output[miner_wallet.address] == MINING_REWARD
