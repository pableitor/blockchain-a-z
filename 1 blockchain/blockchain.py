# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 19:55:53 2021

@author: ptorr
"""
# Modulo 1 Crear Blockchain

# Instalar:
# Flask ==1.1.2 pip install Flask==1.1.2
# Cliente HTTP Postman: https://www.getpostman.com

# para levantar la app sobre Flask:
# > set FLASK_APP=blockchain (nombre del archivo *.py)
# > flask run
#  * Running on http://127.0.0.1:5000/


# Importamos  librerías
import datetime
import hashlib
import json
from flask import Flask, jsonify
# Parte 1 - Crear Cadena de bloques
zeros = '0000'
class Blockchain:
    
    def __init__(self):
        self.chain = [] #lista conteniendo los bloques del blockchain
        self.create_block(proof = 1, previous_hash = '0')                

    
    def create_block(self, proof, previous_hash):
        #create_block : funcion que crea un bloque, en este caso el blq. genesis
        #proof: proof of work, identificador del bloque
        #previous_hash: identificador bloque previo (hash)
        block = { 'index': len(self.chain) + 1, #posicion bloque dentro de la cadena
                 'timestamp': str(datetime.datetime.now()),  #momento en el que el bloque ha sido minado
                 'proof': proof, #proof of work , create_block es llamada despues del minado
                 'previous_hash': previous_hash 
                 }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        #obtener el ultimo bloque de la cadena
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        #calcula el proof of work
        new_proof = 1 #valor de prueba para solucionar el problema, se ira incrementando de uno en uno
        check_proof = False #True si el valor new_proof resuelve el problema
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            #string de num. hex con el resultado de la prueba. La prueba no puede ser simetrica
            #el resultado debe ser stringificado y codificado para calcular el hash
            if hash_operation[:4] == zeros:
                check_proof = True
            else:
                new_proof += 1
        return new_proof
        
    def hash(self, block):
        #toma un bloque de la cadena y devuelve el hash256
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        #chequea blockchain es valido
         previous_block = chain[0]
         block_index = 1
         while block_index < len(chain): #chequeamos bloques uno a uno
             block = chain[block_index]  #referencia al bloque actual
             if block['previous_hash'] != self.hash(previous_block):
                 #calculamos hash del bloque previo y comparamos con el valor almacenado en el bloque
                 return False #si no coinciden los hash , saltamos las alarmas
             previous_proof = previous_block['proof']
             proof = block['proof']
             hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
             #comprobamos que el proof es valido
             if hash_operation[:4] != zeros:
                 return False
             previous_block = block
             block_index += 1
         return True
        
# Parte 2 - Minado de un bloque de la cadena

# Crear web app basada en Flask

#App test: para probar que el servidor funciona abrir http://localhost:5000/ y deberia salir 'Hello World'
app = Flask(__name__)
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
@app.route('/')
def hello():
    return "<p>Hello, World!</p>"
    
# Crear una blockchain

blockchain = Blockchain()

# Minar un nuevo bloque
@app.route('/mine_block', methods=['GET'])
def mine_block(): #definimos la funcion respuesta a http://.../mine_block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash) #guardamos el nuevo bloque
    response = {'message': 'Enhorabuena, has minado un nuevo bloque !!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response),200 #devolvemos los datos del nuevo block y el codigo HTTP 200 ( OK)

# Obtener la cadena de bloques al completo
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Verificar la cadena de bloques es valida
@app.route('/is_valid' , methods=['GET']) 
def check_chain():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        result = 'Blockchain OK'
    else:
        result = 'Blockchain ERROR'
    response = {'result': result}
    return jsonify(response), 200

# Ejecutar la app
app.run(host = '0.0.0.0', port=5000)



