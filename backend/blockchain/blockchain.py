""" blockchain implementations """
from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.config import MINING_REWARD_INPUT, MINING_REWARD
from backend.wallet.wallet import Wallet


class Blockchain:
    """
    Blockchain: a publick ledger of transactions.
    Implemented as a list of blocks - data sets of transactions
    """

    def __init__(self) -> None:
        self.chain = [Block.genesis()]

    def add_block(self, data):
        """adding data to blockchain"""

        self.chain.append(Block.mine_block(self.chain[-1], data))

    def __repr__(self) -> str:
        return f"Blockchain: {self.chain}"

    def replace_chain(self, chain):
        """
        Replace the local chain with the incoming one if the following applies:

        - The incoming chain is longer than the local one.
        - The incoming chain is formatted properly
        """
        if len(chain) <= len(self.chain):
            raise Exception("Cannot replace, the incoming chain must be longer")

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e:
            raise Exception(f"Cannot replce. The incoming chain is invalid: {e}")

        self.chain = chain

    def serialize(self):
        """serialize the blockchain in to loist of blocks"""

        return list(map(lambda block: block.serialize(), self.chain))

    @staticmethod
    def from_json(chain_json):
        """
        Desearialize a list of serialized blocks in to a blockchain instance.
        The result will contain a chain list of Block instance
        """
        blockchain = Blockchain()
        blockchain.chain = list(
            map(lambda block_json: Block.from_json(block_json), chain_json)
        )
        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate the incoming chain.
        Enforced the following rules of the blockchain
        - the chain starts with benesis block
        - block must be formatted correctly
        """

        if chain[0] != Block.genesis():
            raise Exception("The genesis block must be valid")

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i - 1]

            Block.is_valid_block(last_block, block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce the rules of the chain composed of blocks of transactions.
            - Each transaction must only appear once in the chain
            - There can be only on mining reward per block
            - Each transaction must be valid
        """

        transaction_ids = set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False
            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f"Transaction {transaction.id} is not unique")
                transaction_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(
                            "There can only be one mining reward per a block"
                            f"Check block with hash: {block.hash}"
                        )
                    has_mining_reward = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]
                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain, transaction.input["address"]
                    )
                    if historic_balance != transaction.input["ammount"]:
                        raise Exception(
                            f"Transaction {transaction.id} has invalid input amount"
                        )
                Transaction.is_valid_transaction(transaction)


def main():
    blockchain = Blockchain()
    blockchain.add_block("one")
    blockchain.add_block("two")

    print(blockchain)

    print(f"blockchain.py __name__: {__name__}")


if __name__ == "__main__":
    main()
