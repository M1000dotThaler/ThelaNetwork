

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
    
    MINER_REWARD_SIGNATURE = 'miner_reward_signature'  # Firma especial para las transacciones de recompensa del minero
    

    miner_address = None

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()
        self.connect_to_initial_nodes()
        self.wallets = {}
        self.reward_interval = 1000  # Intervalo de bloques para reducir la recompensa
        self.halving_factor = 2  # Factor de reducción de la recompensa
        self.reward = 30 
        

        if not Blockchain.miner_address:
            Blockchain.miner_address = self.generate_wallet()
            print(f"Billetera del minero generada inicialmente: {Blockchain.miner_address}")
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else: 
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount, signature):
     sender_wallet = self.wallets.get(sender)
     receiver_wallet = self.wallets.get(receiver)
    
     if sender == 'network':
        # No es necesario verificar la firma para la transacción del minero
        pass
     else:
        if sender_wallet is None or receiver_wallet is None:
            return 'Billetera de remitente o destinatario no encontrada.'

        if sender_wallet['balance'] < amount:
            return 'Saldo insuficiente para realizar la transacción.'
        
        if not rsa.verify(json.dumps({'sender': sender, 'receiver': receiver, 'amount': amount}), signature, sender_wallet['public_key']):
            return 'Firma digital no válida.'

     # Agregar la transacción a la lista de transacciones pendientes
     self.transactions.append({
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'signature': signature
      })

     # Actualizar los saldos de las billeteras
     if sender != 'network':
       sender_wallet['balance'] -= amount
       receiver_wallet['balance'] += amount

     # Devolver el índice del bloque que contendrá esta transacción
     return self.get_previous_block()['index'] + 1







     # Resto del código sigue igual...
    
    def generate_signature(self, private_key, data):
      # Firmar los datos utilizando la clave privada
     return rsa.sign(json.dumps(data), private_key, 'SHA-256')




    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
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

    def announce_new_block(self, new_block):
        for node in self.nodes:
            requests.post(f'http://{node}/receive_new_block', json={'new_block': new_block})
    
    def connect_to_initial_nodes(self):
        initial_nodes = ['http://192.128.0.100:5000', 'http://localhost:5001', 'http://localhost:5002']
        for node in initial_nodes:
            self.add_node(node)
    
    def generate_wallet(self):
        # Generar un par de claves público-privado
        (public_key, private_key) = rsa.newkeys(512)
        # Calcular la dirección de la billetera a partir del hash de la clave pública
        address = hashlib.sha256(public_key.save_pkcs1()).hexdigest()
        # Inicializar el saldo de la billetera en 0
        self.wallets[address] = {'public_key': public_key, 'private_key': private_key, 'balance': 0}
        # Guardar la clave privada en un archivo local

        print(f'Billetera generada para el minero: {address}')
        self.save_private_key(address, private_key)

        return address
    
    def load_wallets(self):
        # Cargar las claves privadas de las billeteras existentes
        for filename in os.listdir('.'):
            if filename.startswith('private_key_') and filename.endswith('.pem'):
                address = filename.replace('private_key_', '').replace('.pem', '')
                with open(filename, 'rb') as file:
                    private_key = rsa.PrivateKey.load_pkcs1(file.read())
                self.wallets[address] = {'private_key': private_key}
                print(f'Clave privada cargada para la billetera: {address}')
    
    def save_private_key(self, address, private_key):
        filename = f"private_key_{address}.pem"  # Nombre del archivo basado en la dirección de la billetera
        with open(filename, 'wb') as file:
            file.write(private_key.save_pkcs1()) 
    
    def replace_chain_periodically():
     while True:
      time.sleep(1500)  # Esperar 5 segundos
      Blockchain.replace_chain()