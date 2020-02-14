# Paste your version of blockchain.py from the basic_block_gp
# folder here.

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block.
        # This is the start of the chain (the initial block).
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain.

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]), 
        }

        # Reset the current list of transactions.
        self.current_transactions = []

        # Append the block to the chain.
        self.chain.append(block)

        # Return the new block.
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block.

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string.
        # Use hashlib.sha256 to create a hash.
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the dictionary is ordered,
        # or we'll have inconsistent hashes.

        # CONVERTING THE DATA INTO A STRING AND GETTING IT
        # INTO A FORM THAT WE CAN HASH.
        # Create the string object.
        # dumps - stringifies the object
        # sort keys - makes sure that the keys are in the same order
        string_object = json.dumps(block, sort_keys=True)

        # Create the block_string.
        # It's a bytes object now after encoding.
        block_string = string_object.encode()

        # We're now ready to hash now that it's a bytes object.
        # Hash this string using sha256.
        hash_object = hashlib.sha256(block_string)

        # GETTING THE HASH STRING BACK.
        # Call hexdigest to give us a string.
        hash_string = hash_object.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand.

        # Return the hashed block string in hexadecimal format.
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid.
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`.
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise.
        """
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:6] == "000000"


# Instantiate our Node.
app = Flask(__name__)

# Generate a globally unique address for this node.
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain.
blockchain = Blockchain()

@app.route('/last_block', methods=['GET'])
def last_block():
    last_block = blockchain.lastblock
    response = {'last_block': last_block}
    return jsonify(response), 200


@app.route('/mine', methods=['POST'])
def mine():
    """Returns the block we just mined."""

    data = request.get_json()

    # Check that proof and data are both present.
    

    if 'proof' not in data or 'id' not in data:
        response = {'message': 'Missing a required property.'}
        return jsonify(response), 400

    proof = data['proof']
    miner_id = data['id']

    block_string = json.dumps(blockchain.last_block, sort_keys=True)

    # Only forge the new block if we have a valid proof...
    if blockchain.valid_proof(block_string, proof):


        # Forge the new Block by adding it to the chain with the proof.

        previous_hash = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(proof, previous_hash)

        response = {
            # Send a JSON response with the new block.
            # 'block': new_block
            'message': 'New Block Forged',
            'index': new_block['index'],
            'transactions': new_block['transactions'],
            'proof': new_block['proof'],
            'previous_hash': new_block['previous_hash'],
        }

        return jsonify(response), 200

    else:
        response = {'message': 'Proof is invalid or the proof has already been submitted (stale block).'}

        return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # Return the chain and its current length.
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


# Run the program on port 5000.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)