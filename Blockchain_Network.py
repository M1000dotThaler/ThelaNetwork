import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
import rsa
import os
import sys
from urllib.parse import urlparse
import threading
import time

class Blockchain:
    
    MINER_REWARD_SIGNATURE = 'miner_reward_signature'  # Signature of the network to the miner 

    miner_address = None  # Store miner's address

    def __init__(self):
        self.chain = []  # Initialize blockchain as empty list
        self.transactions = []  # Initialize transactions as empty list
        self.create_block(proof=1, previous_hash='0')  # Create genesis block
        self.nodes = set()  # Initialize set of nodes
        self.connect_to_initial_nodes()  # Connect to initial nodes
        self.wallets = {}  # Initialize wallets as empty dictionary
        self.reward_interval = 1000  # Every 1000 blocks mined, the reward is halved
        self.halving_factor = 2  # Factor by which reward is halved
        self.reward = 30  # Initial reward for mining a block

        # Generate miner's wallet if not already generated
        if not Blockchain.miner_address:
            Blockchain.miner_address = self.generate_wallet()
            print(f"Miner wallet generated: {Blockchain.miner_address}")

    # Create a new block in the blockchain
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []  # Clear transactions list after adding to block
        self.chain.append(block)  # Add block to the chain
        return block
        

    # Retrieve the previous block in the chain
    def get_previous_block(self):
        return self.chain[-1]

    # Proof of work algorithm to mine a new block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # Hash operation to find a valid proof
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':  # Check if proof meets difficulty criteria
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    # Hash a block using SHA-256
    def hash(self, block):
        print(block)
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Check if the blockchain is valid
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # Check if previous hash matches the hash of previous block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            # Check if proof of work is valid
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # Add a transaction to the list of transactions
    def add_transaction(self, sender, receiver, amount, signature):
        sender_wallet = self.wallets.get(sender)
        receiver_wallet = self.wallets.get(receiver)

        if sender == 'network':
            # No need to verify signature for miner's transaction
            pass
        else:
            if sender_wallet is None or receiver_wallet is None:
                return 'Sender or receiver wallet not found.'

            if sender_wallet['balance'] < amount:
                return 'Insufficient balance to perform transaction.'
            
            # Verify digital signature
            if not rsa.verify(json.dumps({'sender': sender, 'receiver': receiver, 'amount': amount}).encode('utf-8'), signature, sender_wallet['public_key']):
                return 'Invalid digital signature.'

        # Add transaction to pending transactions list
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'signature': signature
        })

        # Update wallet balances
        if sender != 'network':
            sender_wallet['balance'] -= amount
            receiver_wallet['balance'] += amount

        # Return the index of the block that will contain this transaction
        return self.get_previous_block()['index'] + 1

    # Generate a digital signature using private key
    def generate_signature(self, private_key, data):
        return rsa.sign(json.dumps(data), private_key, 'SHA-256')

    # Add a node to the set of nodes
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Replace the chain with the longest valid chain in the network
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    # Announce the arrival of a new block to all nodes in the network
    def announce_new_block(self, new_block):
        for node in self.nodes:
            requests.post(f'http://{node}/receive_new_block', json={'new_block': new_block})

    # Connect to initial nodes when blockchain is initialized
    def connect_to_initial_nodes(self):
        initial_nodes = ['http://192.128.0.100:5000', 'http://localhost:5001', 'http://localhost:5002']
        for node in initial_nodes:
            self.add_node(node)

    # Generate a wallet for the miner
    def generate_wallet(self):
        # Generate public-private key pair
        (public_key, private_key) = rsa.newkeys(512)
        # Calculate wallet address from public key hash
        address = hashlib.sha256(public_key.save_pkcs1()).hexdigest()
        # Initialize wallet balance to 0
        self.wallets[address] = {'public_key': public_key, 'private_key': private_key, 'balance': 0}
        # Save private key to a local file
        print(f'Wallet generated for miner: {address}')
        self.save_private_key(address, private_key)
        return address

    # Load existing wallets' private keys
    def load_wallets(self):
        for filename in os.listdir('.'):
            if filename.startswith('private_key_') and filename.endswith('.pem'):
                address = filename.replace('private_key_', '').replace('.pem', '')
                with open(filename, 'rb') as file:
                    private_key = rsa.PrivateKey.load_pkcs1(file.read())
                self.wallets[address] = {'private_key': private_key}
                print(f'Private key loaded for wallet: {address}')

    # Save private key to a file
    def save_private_key(self, address, private_key):
        filename = f"private_key_{address}.pem"  # File name based on wallet address
        with open(filename, 'wb') as file:
            file.write(private_key.save_pkcs1())

    # Replace chain periodically
    def replace_chain_periodically():
        while True:
            time.sleep(1500)  # Wait for 5 seconds
            Blockchain.replace_chain()
