""" blcok file """

import time
from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binry
from backend.config import MINE_RATE

GENESIS_DATA = {
    "timestamp": 1,
    "last_hash": "genesis_last_hase",
    "hash": "genesis_hash",
    "data": [],
    "defficulty": 4,
    "nonce": "genesis_nonce",
}


class Block:
    """
    Block: a unit of storage

    Store transactions in a blockchain that supports a cryptocurrency
    """

    def __init__(self, timestamp, last_hash, hash, data, defficulty, nonce) -> None:
        self.timestamp = timestamp
        self.last_hash = last_hash
        self.hash = hash
        self.data = data
        self.defficulty = defficulty
        self.nonce = nonce

    def __repr__(self) -> str:
        return f"Block(timestamp: {self.timestamp}, lash_hash: {self.last_hash}, hash: {self.hash}, data: {self.data}), defficulty: {self.defficulty}, nonce: {self.nonce}"

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def serialize(self):
        return self.__dict__

    @staticmethod
    def mine_block(last_block, data):
        """Mine a block based on a given last_block and data, until the block hash is found that meets
        the leading 0's proof of work requirement
        """
        timestamp = time.time_ns()
        last_hash = last_block.hash
        defficulty = Block.adjuest_defficulty(last_block, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, last_hash, data, defficulty, nonce)

        while hex_to_binry(hash)[0:defficulty] != "0" * defficulty:
            nonce += 1
            timestamp = time.time_ns()
            defficulty = Block.adjuest_defficulty(last_block, timestamp)
            hash = crypto_hash(timestamp, last_hash, data, defficulty, nonce)

        return Block(timestamp, last_hash, hash, data, defficulty, nonce)

    @staticmethod
    def genesis():
        """generate the genesis block"""
        return Block(**GENESIS_DATA)

    @staticmethod
    def from_json(block_json):
        """
        Deserialize the json in to block instance
        """
        return Block(**block_json)

    @staticmethod
    def adjuest_defficulty(last_block, new_timestamp):
        """
        calculate the adjuested defficulty according to the MINE_RATE

        Increase the defficulty for quickly mined blocks.
        Decrese the defficuly for the slowly mined blocks
        """

        if (new_timestamp - last_block.timestamp) < MINE_RATE:
            return last_block.defficulty + 1

        if (last_block.defficulty - 1) > 0:
            return last_block.defficulty - 1

        return 1

    @staticmethod
    def is_valid_block(last_block, block):
        """
        validate a block by enforcing by the following rules
        - the block must have the porper last_hash referenc
        - the block must meet the proof of work requierments
        - the deficulty must only adjuest by1
        - the block hash must be a valid combination of the block field
        """

        if block.last_hash != last_block.hash:
            raise Exception("The block last_hash must be correct")

        if hex_to_binry(block.hash)[0 : block.defficulty] != "0" * block.defficulty:
            raise Exception("The proof of requirement was not met")

        if abs(last_block.defficulty - block.defficulty) > 1:
            raise Exception("The block defficulty must only adjuest by 1")

        reconstructed_hash = crypto_hash(
            block.timestamp,
            block.last_hash,
            block.data,
            block.nonce,
            block.defficulty,
        )

        if block.hash != reconstructed_hash:
            raise Exception("Block hash must be correct")


def main():
    gen_block = Block.genesis()
    bad_block = Block.mine_block(gen_block, "foo")

    # bad_block.last_hash = "evil_data"
    try:
        Block.is_valid_block(gen_block, bad_block)
    except Exception as e:
        print(f"is_valide_block: {e}")


if __name__ == "__main__":
    main()
