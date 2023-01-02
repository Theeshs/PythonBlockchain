import uuid
import time
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


class Transaction:
    """
    Document of an exchange in currency from a sender to one or more
    recipients
    """

    def __init__(
        self,
        sender_wallet=None,
        recipient=None,
        ammount=None,
        id=None,
        output=None,
        input=None,
    ) -> None:
        self.id = id or str(uuid.uuid4())[0:8]
        self.output = output or self.create_output(sender_wallet, recipient, ammount)
        self.input = input or self.create_input(sender_wallet, self.output)

    def create_output(self, sender_wallet, recipient, ammount):
        """
        Structure the output data for the transaction
        """
        if ammount > sender_wallet.balance:
            raise Exception("Amount exceeds balance")
        output = {}
        output[recipient] = ammount
        output[sender_wallet.address] = sender_wallet.balance - ammount

        return output

    def create_input(self, sender_wallet, output):
        """
        Structure the input data for the transaction.
        Sign the transaction and include the sender's public key and address
        """

        return {
            "timestamp": time.time_ns(),
            "ammount": sender_wallet.balance,
            "address": sender_wallet.address,
            "public_key": sender_wallet.public_key,
            "signature": sender_wallet.sign(output),
        }

    def update(self, sender_wallet, recipient, ammount):
        """
        Updated the transaction with existing or new recipient
        """
        if ammount > self.output[sender_wallet.address]:
            raise Exception("Amount exceeds balance")

        if recipient in self.output:
            self.output[recipient] = self.output[recipient] + ammount
        else:
            self.output[recipient] = ammount

        self.output[sender_wallet.address] = (
            self.output[sender_wallet.address] - ammount
        )

        self.input = self.create_input(sender_wallet, self.output)

    def serialize(self):
        return self.__dict__

    def from_json(transaction_json):
        """
        Desrializing the transactions
        """
        return Transaction(**transaction_json)

    @staticmethod
    def is_valid_transaction(transaction):
        """
        validated transaction and raise exception of invalid
        transactions
        """

        if transaction.input == MINING_REWARD_INPUT:
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception("Invalid mining reward")
            return

        output_total = sum(transaction.output.values())
        if transaction.input["ammount"] != output_total:
            raise Exception("Invalid transaction output values")

        if not Wallet.verify(
            transaction.input["public_key"],
            transaction.output,
            transaction.input["signature"],
        ):
            raise Exception("Invalid Signature")

    @staticmethod
    def reward_transaction(miner_wallet):
        """
        Generate reward transaction that award the miner
        """
        output = {}
        output[miner_wallet.address] = MINING_REWARD

        return Transaction(input=MINING_REWARD_INPUT, output=output)


def main():
    trasaction = Transaction(Wallet(), "recipient", 15)
    print(f"trasaction: {trasaction.__dict__}")
    trasaction_json = trasaction.serialize()
    restored_transaction = Transaction.from_json(trasaction_json)
    print(f"restored_transaction: {restored_transaction.__dict__}")


if __name__ == "__main__":
    main()
