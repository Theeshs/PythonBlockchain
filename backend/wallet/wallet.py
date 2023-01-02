import uuid
import json
from backend.config import STARTING_BALANCE
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature,
    decode_dss_signature,
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class Wallet:
    """
    An individual wallet for a miner.
    Keep track of the miner's balance.
    Allow a miner to authorize transaction
    """

    def __init__(self, blockchain=None) -> None:
        self.blockchain = blockchain
        self.address = str(uuid.uuid4())[0:8]
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        self.serialize_public_key()

    @property
    def balance(self):
        return Wallet.calculate_balance(self.blockchain, self.address)

    def sign(self, data):
        """generate the signature based on the given data and local private key"""
        # print(data)
        # print(json.dumps(data))
        return decode_dss_signature(
            self.private_key.sign(
                json.dumps(data).encode("utf-8"), ec.ECDSA(hashes.SHA256())
            )
        )

    def serialize_public_key(self):
        """serializing the public key"""
        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    @staticmethod
    def verify(public_key, data, signature):
        """verify the signature based on the data and original public key"""
        deserialized_public_key = serialization.load_pem_public_key(
            public_key.encode("utf-8"), default_backend()
        )
        (r, s) = signature
        try:
            deserialized_public_key.verify(
                encode_dss_signature(r, s),
                json.dumps(data).encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def calculate_balance(blockchain, address):
        """
        Calculate the balance of the given address considering the transaction data within the
        blockchain

        The balance is found by adding the output values that belongs to the address since the most
        recent transaction by that address
        """

        balance = STARTING_BALANCE

        if not blockchain:
            return balance

        for block in blockchain.chain:
            for transaction in block.data:
                if transaction["input"]["address"] == address:
                    # any thiem the address conducts an new transaction it reset
                    # its balance
                    balance = transaction["output"][address]
                elif address in transaction["output"]:
                    balance += transaction["output"][address]
        return balance


def main():
    wallet = Wallet()
    print(f"Wallet: {wallet.__dict__}")

    data = {"foo": "bar"}

    signature = wallet.sign(data)
    print(f"signature: {signature}")

    should_be_valid = wallet.verify(wallet.public_key, data, signature)
    print(f"should_be_valid: {should_be_valid}")

    should_be_not_valid = wallet.verify(Wallet().public_key, data, signature)
    print(f"should_be_valid: {should_be_not_valid}")


if __name__ == "__main__":
    main()
