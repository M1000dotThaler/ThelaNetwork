
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
from Blockchain_Network import Blockchain


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Reducir la recompensa si corresponde
    if len(blockchain.chain) % blockchain.reward_interval == 0:
        blockchain.reward /= blockchain.halving_factor  # Reducir la recompensa a la mitad
    
    reward = blockchain.reward
    miner_address = request.args.get('miner_address')  # Obtener la dirección del minero de los parámetros de la solicitud
    blockchain.add_transaction(sender='network', receiver=Blockchain.miner_address, amount=reward, signature=Blockchain.MINER_REWARD_SIGNATURE)  # No se necesita firma para la recompensa del minero
    blockchain.wallets[Blockchain.miner_address]['balance'] += reward
    
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': '¡Enhorabuena, has minado un nuevo bloque!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }

    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/receive_new_block', methods=['POST'])
def receive_new_block():
    new_block = request.json['new_block']
    blockchain.chain.append(new_block)
    response = {'message': 'El bloque ha sido agregado a la cadena'}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Todo correcto. La cadena de bloques es válida.'}
    else:
        response = {'message': 'Houston, tenemos un problema. La cadena de bloques no es válida.'}
    return jsonify(response), 200  



@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json_data = request.get_json()
    
    # Verificar si se proporcionaron todos los campos necesarios
    if not all(key in json_data for key in ['sender', 'receiver', 'amount']):
        return jsonify({'message': 'Todos los campos (sender, receiver, amount) son requeridos'}), 400

    # Verificar si los campos tienen el tipo de datos correcto
    sender = json_data.get('sender')
    receiver = json_data.get('receiver')
    amount = json_data.get('amount')
    if not isinstance(amount, (int, float)):
        return jsonify({'message': 'El campo "amount" debe ser un número'}), 400

    # Obtener la clave privada del remitente
    sender_wallet = blockchain.wallets.get(sender)
    if sender_wallet is None:
        return jsonify({'message': 'Billetera de remitente no encontrada'}), 404
    private_key = sender_wallet['private_key']

    # Firmar la transacción
    signature = rsa.sign(json.dumps({'sender': sender, 'receiver': receiver, 'amount': amount}), private_key, 'SHA-256')

    # Agregar la transacción utilizando los datos proporcionados y la firma
    result = blockchain.add_transaction(sender, receiver, amount, signature)
    if isinstance(result, int):
        response = {'message': 'Transacción agregada al bloque pendiente.', 'block_index': result}
        return jsonify(response), 201
    else:
        return jsonify({'message': result}), 400






@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_data = request.get_json()
    nodes = json_data.get('nodes')
    if nodes is None: 
        return 'No hay nodos para añadir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'Todos los nodos han sido conectados. La cadena de bloques contiene ahora los nodos siguientes: ',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'Los nodos tenían diferentes cadenas, que han sido todas reemplazadas por la más larga.',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Todo correcto. La cadena en todos los nodos ya es la más larga.',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), 200  

@app.route('/generate_wallet', methods=['GET'])
def generate_wallet_route():
    address = blockchain.generate_wallet()
    response = {'message': 'Billetera generada exitosamente', 'address': address}
    return jsonify(response), 200

@app.route('/check_balance/<address>', methods=['GET'])
def check_balance(address):
    wallet = blockchain.wallets.get(address)
    if wallet:
        balance = wallet.get('balance', 0)
        response = {'message': 'Saldo consultado correctamente', 'address': address, 'balance': balance}
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Billetera no encontrada'}), 404
    

replace_chain_thread = threading.Thread(target=Blockchain.replace_chain_periodically)
replace_chain_thread.daemon = True  # El hilo se detendrá cuando el programa principal termine
replace_chain_thread.start()
print("se ha actualizado la blockchain")


if __name__ == '__main__':
    # Se verifica si se especificó una dirección de minero al iniciar el nodo
    if len(sys.argv) > 1:
        # Si se especificó una dirección del minero, utilizarla
        node_address = sys.argv[1]
        print("Dirección del minero:", node_address)
    else:
        # Si no se especificó una dirección del minero, generar una billetera automáticamente
        node_address = blockchain.generate_wallet()
        print("Dirección de la billetera generada automáticamente:", node_address)

    app.run(host='0.0.0.0', port=5000)


