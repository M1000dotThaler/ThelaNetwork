from flask import Flask, jsonify, request
import threading
import sys
import time
import rsa
import json
import base64

# Import the Blockchain class from blockchain.py file
from Blockchain_Network import Blockchain

# Create a Flask app instance
app = Flask(__name__)

# Configure JSONIFY_PRETTYPRINT_REGULAR to False to avoid pretty printing JSON responses
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Instantiate the Blockchain class
blockchain = Blockchain()

# Route to mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # Get the previous block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Reduce the reward if applicable
    if len(blockchain.chain) % blockchain.reward_interval == 0:
        blockchain.reward /= blockchain.halving_factor  # Reduce the reward by half
    
    reward = blockchain.reward
    miner_address = request.args.get('miner_address')  # Get the miner's address from the request parameters
    # Add a transaction to reward the miner
    blockchain.add_transaction(sender='network', receiver=Blockchain.miner_address, amount=reward, signature=Blockchain.MINER_REWARD_SIGNATURE)  # No signature needed for miner reward
    blockchain.wallets[Blockchain.miner_address]['balance'] += reward
    
    # Create the new block
    block = blockchain.create_block(proof, previous_hash)

    # Convert transactions to a serializable format (list of dictionaries)
    transactions = block['transactions']
    for transaction in transactions:
     if isinstance(transaction['signature'], str):
        signature_base64 = transaction['signature']
     else:
        signature_base64 = base64.b64encode(transaction['signature']).decode()  # Encode signature to base64
     transaction['signature'] = signature_base64  
        

    response = {
        'message': 'Congratulations, you have mined a new block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': transactions
    }

    return jsonify(response), 200

# Route to get the entire blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

# Route to receive a new block from other nodes
@app.route('/receive_new_block', methods=['POST'])
def receive_new_block():
    new_block = request.json['new_block']
    blockchain.chain.append(new_block)
    response = {'message': 'The block has been added to the blockchain'}
    return jsonify(response), 200

# Route to check if the blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Everything is fine. The blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The blockchain is not valid.'}
    return jsonify(response), 200  

# Route to add a new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json_data = request.get_json()
    
    # Check if all required fields are provided
    if not all(key in json_data for key in ['sender', 'receiver', 'amount']):
        return jsonify({'message': 'All fields (sender, receiver, amount) are required'}), 400

    # Check if fields have correct data type
    sender = json_data.get('sender')
    receiver = json_data.get('receiver')
    amount = json_data.get('amount')
    if not isinstance(amount, (int, float)):
        return jsonify({'message': 'The "amount" field must be a number'}), 400

    # Get the sender's private key
    sender_wallet = blockchain.wallets.get(sender)
    if sender_wallet is None:
        return jsonify({'message': 'Sender wallet not found'}), 404
    private_key = sender_wallet['private_key']

    # Sign the transaction
    signature = rsa.sign(json.dumps({'sender': sender, 'receiver': receiver, 'amount': amount}).encode('utf-8'), private_key, 'SHA-256')

    # Add the transaction using provided data and signature
    result = blockchain.add_transaction(sender, receiver, amount, signature)
    if isinstance(result, int):
        response = {'message': 'Transaction added to pending block.', 'block_index': result}
        return jsonify(response), 201
    else:
        return jsonify({'message': result}), 400

# Route to connect a new node to the network
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_data = request.get_json()
    nodes = json_data.get('nodes')
    if nodes is None: 
        return 'No nodes to add', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'All nodes have been connected. The blockchain now contains the following nodes: ',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

# Route to replace the chain with the longest valid chain in the network
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'Nodes had different chains, all replaced by the longest one.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Everything is fine. Chain in all nodes is already the longest one.',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), 200  

# Route to generate a wallet address
@app.route('/generate_wallet', methods=['GET'])
def generate_wallet_route():
    address = blockchain.generate_wallet()
    response = {'message': 'Wallet generated successfully', 'address': address}
    return jsonify(response), 200

# Route to check balance of a given wallet address
@app.route('/check_balance/<address>', methods=['GET'])
def check_balance(address):
    wallet = blockchain.wallets.get(address)
    if wallet:
        balance = wallet.get('balance', 0)
        response = {'message': 'Balance queried successfully', 'address': address, 'balance': balance}
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Wallet not found'}), 404

# Start a thread to periodically replace the chain
replace_chain_thread = threading.Thread(target=Blockchain.replace_chain_periodically)
replace_chain_thread.daemon = True  # Thread will stop when the main program ends
replace_chain_thread.start()
print("Blockchain has been updated")

# Run the Flask app
if __name__ == '__main__':
    # Check if a miner address was specified when starting the node
    if len(sys.argv) > 1:
        # If a miner address was specified, use it
        node_address = sys.argv[1]
        print("Miner Address:", node_address)
    else:
        # If no miner address was specified, generate a wallet automatically
        node_address = blockchain.generate_wallet()
        print("Automatically Generated Wallet Address:", node_address)

    # Run the app on host '0.0.0.0' and port 5000
    app.run(host='0.0.0.0', port=5000)
