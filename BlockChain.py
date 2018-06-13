import time
import random
import requests
from hashlib import sha256
from functools import reduce
from flask import Flask
from flask import request
from flask import abort
import json


class BlockChain:

    def __init__(self):
        self.__chain = []
        self.__transactions = [] # transaction list. should be a set
        self.__neighborNodes = set() #Addresses of the peer nodes connected to this one
        self.__neighborNodes.add("http://127.0.0.1:5001")
        #self.__neighborNodes.add("http://127.0.0.1:5002")
        self.__bits = 6 # init the number of bits for proof of work validation
        self.__chain.append({
            "merkleTree":"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
            "bits": self.__bits,
            "nounce": int(random.random()*100),
            "time": time.time(),
            "version": 1,
            "hash": sha256("Tiisetso-tjabane-31_May_2018").hexdigest()
        })

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
        validation  = reduce((lambda x, y: x + y), ["0"] * self.__bits)
        currentBlockHash = sha256(str(block)).hexdigest()
        while(not currentBlockHash.startswith(validation)):
            block["nounce"] += 1
            currentBlockHash = sha256(str(block)).hexdigest()
        return currentBlockHash

    #  init for a new block to be made, and once its found it will broadcast it to the rest of the network
    def Mine(self):
        if len(self.__transactions) > 0:
            print "Mining started"
            block = {
                "merkleTree": self.createMerkleTree(self.__transactions),
                "bits": self.__bits,
                "nounce": int(random.random()*100),
                "time": time.time(),
                "version": 1,
                "prev": self.__chain[-1]["hash"]
            }
            block["hash"] = self.createHash(block)
            self.__chain.append(block)
            self.__broadcast(block, isBlock=True, originNode=None)

    #adds new Transactions
    def addTransaction(self, transaction, node=None):
        if(transaction):
            self.__transactions.append(transaction)
            print(self.__transactions)
            self.__broadcast(transaction, isBlock=False, originNode=node)
            if len(self.__transactions) > 6:
                self.Mine()
                self.__transactions = []


    def addBlock(self, Block, node):
        if self.validateBlock(Block):
            self.__chain.append(Block)
        self.__broadcast(Block, isBlock=True, originNode=node)

    def addNode(self, address):
        self.__neighborNodes.append(address)

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

    def __broadcast(self,data, isBlock, originNode = None):
        print("send the new block to all the neighbor nodes")
        results = []
        if originNode:
            self.__neighborNodes.remove(originNode)
        if(isBlock):
            for node in self.__neighborNodes:
                print "%(node)s/block" % locals()
                r = requests.post("%(node)s/block" % locals(), data={'block': json.dumps(data)})
                results.append(r.status_code)
        else:
            for node in self.__neighborNodes:
                r = requests.post("http://127.0.0.1:5002/transactions", data=json.dumps({'transaction': data}))
                print r.status_code, r.reason
                results.append(r.status_code)
        print results




