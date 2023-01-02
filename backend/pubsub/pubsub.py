from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
import time
from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-0b640abe-eb80-4ef4-b9db-6d2536504fee"
pnconfig.publish_key = "pub-c-65116574-c305-45fc-a0f1-5e31234b048e"


CHANNELS = {"TEST": "TEST", "BLOCK": "BLOCK", "TRANSACTION": "TRANSACTION"}


class Listner(SubscribeCallback):
    def __init__(self, blockchain, transaction_pool) -> None:
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        print(
            f"\n-- Channel: {message_object.channel} | Message: {message_object.message}"
        )
        if message_object.channel == CHANNELS["BLOCK"]:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_chain(potential_chain)
                self.transaction_pool.clear_blockchain_transactions(self.blockchain)
                print("\n -- Successfully replace the local chain")
            except Exception as e:
                print(f"\n -- Did not replace the chain: {e}")

        elif message_object.channel == CHANNELS["TRANSACTION"]:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print("\n -- Set the new transaction in the trasaction pool")


class PubSub:
    """
    Handles the publish/subscribe layer of the application.
    provides communitcation between the nodes of the blockchain network
    """

    def __init__(self, blockchain, transaction_pool) -> None:
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listner(blockchain, transaction_pool))

    def publish(self, channel, message):
        """
        publishing the message object to the channel
        """

        self.pubnub.publish().channel(channel).message(message).sync()

    def broadcast_block(self, block):
        """
        Broadcast a block object to all nodes
        """
        self.publish(CHANNELS["BLOCK"], block.serialize())

    def broadcast_transactions(self, transaction):
        """Broadcast a transaction to all nodes"""
        self.publish(CHANNELS["TRANSACTION"], transaction.serialize())


def main():
    pubsub = PubSub()
    time.sleep(1)
    pubsub.publish(CHANNELS["TEST"], {"foo": "bar"})


if __name__ == "__main__":
    main()
