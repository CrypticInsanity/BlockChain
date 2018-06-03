from flask import Flask
from flask import request
from flask import abort
from BlockChain import BlockChain
import validators
import json



app = Flask(__name__)
block = BlockChain()


@app.route('/transactions', methods=["POST"])
def addTransaction():
    try:
        if request.data:
            data = json.loads(request.data)
            block.addTransaction(data["transaction"])
            return "transaction added successfully"
        else:
            return abort(400, "bad request")
    except:
        return abort(501, "internal server error")

@app.route('/block', methods=["POST"])
def addBlock():
    try:
        if request.data:
            data = json.loads(request.data)
            block = json.load(data["block"])
            if block.validateBlock(block):
                block.addBlock(block)
                return "block received successfully"
            else:
                return abort(400, "Invalid block received")
        else:
            return abort(400, "bad request")
    except:
        return abort(501, "internal server error")

@app.route('/register', methods=["POST"])
def registerNode():
    data = json.loads(request.data)
    address = data["address"]
    if validators.url(address):
        block.addNode(address)
        return "node added succesfully"
    else:
        return abort(401, "Invalid address received")

@app.route('/', methods=["GET"])
def index():
    return "Welcome to the sample blockchain, best way to learn something its usually by building it"

config = {
    "port": 5000
}

if __name__ == '__main__':
   app.run(debug=True, port=config["port"])
