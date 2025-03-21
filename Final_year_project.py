import hashlib
import json
import time
import random
import requests
import threading
from flask import Flask, request, jsonify

# Blockchain Class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
    
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
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
        while True:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                return new_proof
            new_proof += 1
    
    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        for i in range(1, len(chain)):
            block = chain[i]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            if not self.proof_of_work(block['proof']):
                return False
            previous_block = block
        return True
    
    def add_transaction(self, device_id, data):
        self.transactions.append({
            'device_id': device_id,
            'data': data
        })
        return self.get_previous_block()['index'] + 1

# Flask App Setup
app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(previous_block['proof'])
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Block Mined', 'index': block['index'], 'transactions': block['transactions']}
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json_data = request.get_json()
    required_fields = ['device_id', 'data']
    if not all(field in json_data for field in required_fields):
        return 'Missing fields', 400
    index = blockchain.add_transaction(json_data['device_id'], json_data['data'])
    return jsonify({'message': f'Transaction added to Block {index}'}), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

# IoT Device Simulation (Proteus Connection)
def simulate_iot_device():
    while True:
        device_id = f"ESP8266_{random.randint(1000, 9999)}"
        data = f"Temperature: {random.randint(20, 30)}°C"
        requests.post('http://127.0.0.1:5000/add_transaction', json={'device_id': device_id, 'data': data})
        time.sleep(5)

if __name__ == '__main__':
    threading.Thread(target=simulate_iot_device).start()
    app.run(debug=True)
