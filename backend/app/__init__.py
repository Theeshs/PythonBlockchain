import os
import requests
import random
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.blockchain.blockchain import Blockchain
from backend.pubsub.pubsub import PubSub
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain=blockchain, transaction_pool=transaction_pool)


@app.route("/")
def route_default():
    return "Welcome to the blockchain"


@app.route("/blockchain")
def route_blockchain():
    return jsonify(blockchain.serialize())


@app.route("/blockchain/range")
def rout_blockchain_range():
    start = int(request.args.get("start"))
    end = int(request.args.get("end"))

    return jsonify(blockchain.serialize()[::-1][start:end])


@app.route("/blockchain/length")
def route_blockchain_length():
    return jsonify(len(blockchain.serialize()))


@app.route("/blockchain/mine")
def route_blockchain_mine():
    transaction_data = transaction_pool.transaction_data()
    transaction_data.append(Transaction.reward_transaction(wallet).serialize())
    blockchain.add_block(transaction_data)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.clear_blockchain_transactions(blockchain)

    return jsonify(block.serialize())


@app.route("/wallet/transact", methods=["POST"])
def route_wallet_transact():
    transaction_data = request.get_json()
    print(transaction_data)
    transaction = transaction_pool.existing_transaction(wallet.address)
    if transaction:
        transaction.update(
            wallet, transaction_data["recipient"], transaction_data["amount"]
        )
    else:
        transaction = Transaction(
            wallet, transaction_data["recipient"], transaction_data["amount"]
        )
    pubsub.broadcast_transactions(transaction)
    return jsonify(transaction.serialize())


@app.route("/wallet/info")
def route_wallet_info():
    return jsonify({"address": wallet.address, "balance": wallet.balance})


@app.route("/known-address")
def route_known_address():
    known_addresses = set()
    for block in blockchain.chain:
        for transac in block.data:
            known_addresses.update(transac["output"].keys())
    return jsonify(list(known_addresses))


@app.route("/transactions")
def rout_trnsactions():
    return jsonify(transaction_pool.transaction_data())


ROOT_PORT = 5000
PORT = ROOT_PORT
# print(type(os.environ.get("PEER")))
if os.environ.get("PEER") == "True":
    PORT = random.randint(5001, 6000)
    result = requests.get(f"http://127.0.0.1:{ROOT_PORT}/blockchain")
    try:
        print(f"result.json(): {result.json()}")
        result_blockchain = Blockchain.from_json(result.json())
        blockchain.replace_chain(result_blockchain.chain)
        print("\n --Successfull Synced the Local chain")
    except Exception as e:
        print(f"\n --Error Syncing: {e}")

if os.environ.get("SEED_DATA") == "True":
    for i in range(10):
        blockchain.add_block(
            [
                Transaction(
                    Wallet(), Wallet().address, random.randint(2, 50)
                ).serialize(),
                Transaction(
                    Wallet(), Wallet().address, random.randint(2, 50)
                ).serialize(),
            ]
        )

    for i in range(3):
        transaction_pool.set_transaction(
            Transaction(Wallet(), Wallet().address, random.randint(2, 50))
        )

app.run(port=PORT)
