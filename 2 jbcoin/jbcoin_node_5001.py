# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 20:22:18 2021

@author: ptorr
"""
# Modulo 2 Crear una criptomoneda


# Instalar:
# Flask ==1.1.2 pip install Flask==1.1.2
# Cliente HTTP Postman: https://www.getpostman.com
# requests==2.18.4 : pip install requests==2.18.4

# para levantar la app sobre Flask:
# > set FLASK_APP=blockchain (nombre del archivo *.py)
# > flask run
#  * Running on http://127.0.0.1:5000/

 
# Importamos  librerías
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Parte 1 - Crear una Cadena de bloques
zeros = '0000'
class Blockchain:
    
    def __init__(self):
        self.chain = [] #lista conteniendo los bloques del blockchain
        self.transactions = [] # lista conteniendo las transacciones
        self.create_block(proof = 1, previous_hash = '0') 
        self.nodes = set() # conjunto actualizable, sin orden,  de los nodos que forman la red blockchain
                     

    
    def create_block(self, proof, previous_hash):
        #create_block : funcion que crea un bloque, en este caso el blq. genesis
        #proof: proof of work, identificador del bloque
        #previous_hash: identificador bloque previo (hash)
        block = { 'index': len(self.chain) + 1, #posicion bloque dentro de la cadena
                 'timestamp': str(datetime.datetime.now()),  #momento en el que el bloque ha sido minado
                 'proof': proof, #proof of work , create_block es llamada despues del minado
                 'previous_hash': previous_hash,
                 'transactions': self.transactions
                 }
        self.transactions = [] #vaciar lista  de transacciones una vez minado el bloque
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
            if hash_operation[:len(zeros)] == zeros:
                check_proof = True
                print("Proof: ", new_proof,"\nHash operation: ", hash_operation)
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
             if hash_operation[:len(zeros)] != zeros:
                 return False
             previous_block = block
             block_index += 1
         return True

    def add_transaction(self, sender, receiver, amount):
         #  formatea y añade las transacciones
         self.transactions.append({'sender':sender,
                                   'receiver': receiver,
                                   'amount': amount})
         previous_block = self.get_previous_block()
         return previous_block['index'] + 1 #devuelve indice de block donde se va a añadir la transaccion

    def add_node( self, address):
        # añade un nodo a la red (en este caso los nodos residen en diferentes puertos de un servidor de nuestra LAN)
        parsed_url = urlparse(address) # parsea la direccion http
        self.nodes.add(parsed_url.netloc) #del resultado del parse solamente utilizaremos la direccion

    def replace_chain(self):  
        #realiza el consenso entre nodos, cada nodo verifica si dispone de la cadena mas larga 
        # en caso contrario actualiza su blockchain . Cada vez que un nodo mina un bloque notifica al resto de los nodos
        network = self.nodes #conjunto de todos los nodos
        longest_chain = None #en este punto hemos minado un bloque pero no sabemos cual es la cadena mas larga
        max_length = len(self.chain) # suponemos que nuestra cadena es la mas larga, salvo que detectemos otra a posteriori
        for node in network: #vamos a pedir la longitud de cadena de cada nodo
            response = requests.get(f'http://{node}/get_chain') # solicita la cadena a la direccion http del nodo
            if response.status_code == 200: # respuesta correcta
                length = response.json()['length'] # guardamos longitud de la cadena enviada por el nodo 
                chain = response.json()['chain'] # recuperamos la cadena del nodo solicitado
                if length > max_length and self.is_chain_valid(chain): #aceptamos que hay una cadena mas larga
                    max_length = length #actualizar valores
                    longest_chain = chain
        if longest_chain: # si hemos encontrado una cadena mas larga que la nuestra
            self.chain = longest_chain     #reemplazamos nuestra cadena con la que hemos encontrado
            return True
        return False
            
# Parte 2 - Minado de un bloque de la cadena

# Crear web app basada en Flask

app = Flask(__name__)
# Si da error 500 descomentar la siguiente linea:
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Crear la dirección del nodo en el puerto 5000
node_address = str(uuid4()).replace('-','') #generamos unique user identifier aleatorio sin guiones

#App test: para probar que el servidor funciona abrir http://localhost:5000/ y deberia salir 'Hello World'

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
    blockchain.add_transaction(sender = node_address, receiver = 'Pablo', amount='10' )
    block = blockchain.create_block(proof, previous_hash) #guardamos el nuevo bloque
    response = {'message': 'Enhorabuena, has minado un nuevo bloque !!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response),200 #devolvemos los datos del nuevo block y el codigo HTTP 200 ( OK)

# Obtener la cadena de bloques al completo
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Verificar la cadena de bloques es valida
@app.route('/is_valid' , methods=['GET']) 
def is_valid():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        result = 'Blockchain OK'
    else:
        result = 'Blockchain ERROR'
    response = {'result': result}
    return jsonify(response), 200


# Añadir una nueva transaccion a la cadena de bloques
@app.route('/add_transaction' , methods=['POST']) # POST transaction data
def add_transaction():
    # cuando llamamos a la funcion POSTeamos por POSTMAN un fichero json con los datos 
    json = request.get_json() #obtener fichero json posteado por POSTMAN
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys): #las 3 claves deben estar en el fichero json
        return 'Error: Falta clave de algun elemento en la transaccion', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount']) 
    # index:indice del bloque de la cadena que contrendra la transaccion cuando el bloque sea minado
    response = {'message': f'La transaccion será añadida al bloque {index}'}
    return jsonify(response), 201 #codigo de respuesta cuando se crea algo a partir de una peticion POST

    

# Parte 3 - Descentralizar la Cadena de Bloques

# Para conectar nuevos nodos:
# enviamos por POST un fichero json con los nodos que vamos a dar de alta
@app.route('/connect_node' , methods=['POST']) # POST transaction data
def connect_node():
    json = request.get_json() #obtener fichero json posteado por POSTMAN
    nodes = json.get('nodes') # procesamos el json para obtener las direcciones de los nodos
    # el formato del json seria : {'nodes':['127.0.0.0:5001', '127.0.0.0:5002',...]}
    if nodes is None:
        return'ERROR: No hay nodos a añadir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'Nodos conectados. La cadena contiene los nodos:',
                'total_nodes': list(blockchain.nodes)} # creamos un diccionario como respuesta
    return jsonify(response ), 201 #codigo de respuesta cuando se crea algo a partir de una peticion POST

# Reemplazar la blockchain por la mas larga (si es necesario)    
@app.route('/replace_chain' , methods=['GET']) 
def replace_chain():
    
    is_chain_replaced = blockchain.replace_chain() #devuelve True si la cadena no es la mas larga y ha sido reemplazada
                                                    #False si ya disponemos de la cadena mas larga      
    if is_chain_replaced:
        response ={'message': 'Los nodos tenian diferentes cadenas, que han sido reemplazadas por la mas larga',
                   'new_chain': blockchain.chain}
    else:
        response = {'message': 'Todo correcto. La cadena en todos los nodos es la mas larga',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Ejecutar la app
app.run(host = '0.0.0.0', port=5001)

