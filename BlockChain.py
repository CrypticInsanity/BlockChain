import time
import random
from hashlib import sha256
from functools import reduce
from flask import Flask
from flask import request
from flask import abort
import json


class BlockChain:

    def __init__(self):
        self.chain = []
        self.transactions = [] # transaction list. should be a set
        self.neighborNodes = [] #Addresses of the peer nodes connected to this one
        self.nounce = int(random.random()*100) # random number that will be used for find the proof of work
        self.bits = 6 # init the number of bits for proof of work validation
        self.chain.append({
            "merkleTree":"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
            "bits": self.bits,
            "nounce": int(random.random()*100),
            "time": time.time(),
            "version": 1
        })
        self.prev = self.createHash(self.chain[-1])

    #builds the merkle tree of the transactions.
    def createMerkleTree(self,transactionsArray):
        temp = []
        size = len(transactionsArray)
        if (size == 1):
            return transactionsArray.pop()
        elif (size % 2 == 0):
            for i in range(0, size - 1, 2):
                temp.append(sha256(transactionsArray[i] + transactionsArray[i + 1]).hexdigest())

            return self.createMerkleTree(temp)
        elif (size % 2 != 0):
            for i in range(0, size - 2, 2):
                temp.append(sha256(transactionsArray[i] + transactionsArray[i + 1]).hexdigest())
            temp.append(transactionsArray[-1])
            return self.createMerkleTree(temp)

    #this is where the actual mining takes place, it incremenets the nounce until a hash with the right number of bits of produced or
    #receives a new block that its currently working on.
    def createHash(self, block):
        validation  = reduce((lambda x, y: x + y), ["0"] * self.bits)
        currentBlockHash = sha256(str(block)).hexdigest()
        while(not currentBlockHash.startswith(validation)):
            block["nounce"] += 1
            currentBlockHash = sha256(str(block)).hexdigest()
        return currentBlockHash

    #  init for a new block to be made, and once its found it will broadcast it to the rest of the network
    def Mine(self):
        if len(self.transactions) > 0:
            block = {
                "merkleTree": self.createMerkleTree(self.transactions),
                "bits": self.bits,
                "nounce": int(random.random()*100),
                "time": time.time(),
                "version": 1,
                "prev": self.createHash(self.chain[-1])
            }
            return self.createHash(block)

    #adds new  Transactions
    def addTransaction(self, transaction):
        if(transaction):
            self.transactions.append(transaction)
            if(len(self.transactions) > 200):
                self.Mine()

    def addBlock(self, Block, node):
        if(self.validateBlock(Block)):
            self.chain.append(Block)
            self.broadcastNewBlock(Block, node)


    def validateBlock(self, newBlock):
        #validate the values
        if(not (newBlock["merkleTree"] and
                (newBlock["bits"] and newBlock["bits"] == self.bits) and
                newBlock["nounce"] and
                newBlock["time"] and
                newBlock["version"] and
                newBlock["prev"] and
                newBlock["hash"]
                )

          ):
            print("Block contains invalid data")
            return False

        if(not newBlock["hash"].startswith(reduce((lambda x, y: x + y), ["0"] * self.bits))):
            print("invalid number of bits")
            return False

        currentMerkleTree = self.createMerkleTree(self, self.transactions)

        if(currentMerkleTree != newBlock["merkleTree"]):
            print("MerkleTree dont match")
            return False
        if(newBlock["prev"] != self.chain[-1]["hash"]):
            print("invalid block for the current chain");
            return False
        else:
            return True

    def broadcastNewBlock(self, Block,Node):
        print("send the new block to all the neighbor nodes")

    def broadcastNewTransaction(self, transaction, originNode ):
        print("Send the newly received transaction to the rest of the network")


app = Flask(__name__)

block = BlockChain()
@app.route('/Chain')
def hello_world():
   return json.dumps(block.chain)


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
        return abort(501,"internal server error")

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
                return abort(400, "Invalid block received");
        else:
            return abort(400, "bad request")
    except:
        return abort(501, "internal server error")

@app.route('/register', methods=["GET"])
def registerNode():
    return "new node added"


if __name__ == '__main__':
   app.run(debug=True)







