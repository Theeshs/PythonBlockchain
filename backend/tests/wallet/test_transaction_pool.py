from backend.wallet.transaction_pool import TransactionPool
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain


def test_set_transation():
    transaction_pool = TransactionPool()
    transaction = Transaction(Wallet(), "reci", 1)
    transaction_pool.set_transaction(transaction)

    assert transaction_pool.transaction_map[transaction.id] == transaction


def test_clear_blockchain_transaction():
    transaction_pool = TransactionPool()
    transaction_1 = Transaction(Wallet(), "recip1", 10)
    transaction_2 = Transaction(Wallet(), "recip2", 20)
    transaction_3 = Transaction(Wallet(), "recip3", 30)

    transaction_pool.set_transaction(transaction_1)
    transaction_pool.set_transaction(transaction_2)
    transaction_pool.set_transaction(transaction_3)

    blockchain = Blockchain()

    blockchain.add_block(
        [
            transaction_1.serialize(),
            transaction_2.serialize(),
            transaction_3.serialize(),
        ]
    )

    assert transaction_1.id in transaction_pool.transaction_map
    assert transaction_2.id in transaction_pool.transaction_map
    assert transaction_3.id in transaction_pool.transaction_map
    transaction_pool.clear_blockchain_transactions(blockchain)

    assert not transaction_1.id in transaction_pool.transaction_map
    assert not transaction_2.id in transaction_pool.transaction_map
    assert not transaction_3.id in transaction_pool.transaction_map
