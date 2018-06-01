from flask import Flask
from flask import request
from flask import abort
import json
from BlockChain import BlockChain

app = Flask(__name__)
block = BlockChain()

@app.route('/transactions', methods=["POST"])
def addTransaction():
    try:
        print request.data
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
            if(block.validateBlock(block)):
                block.addBlock(block)
                return "block received successfully"
            else:
                return abort(400, "Invalid block received")
        else:
            return abort(400, "bad request")
    except:
        return abort(501, "internal server error")

@app.route('/register', methods=["GET"])
def registerNode():
    print request.headers
    return "new node added"


if __name__ == '__main__':
   app.run(debug=True)
