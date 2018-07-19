""" SNAKE COIN SAMPLE NODE
    Based on Gerald Nash's "Let's Make the Tiniest Blockchain Bigger"
    https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
    https://gist.github.com/aunyks/47d157f8bc7d1829a729c2a6a919c173

    Adapted to my own style preferences.
"""

from flask import Flask
from flask import request
node = Flask(__name__)

import datetime as date
import hashlib as hasher
import json


class Block(object):
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hasher()

  def hasher(self):
    sha = hasher.sha256()
    sha.update(str(self.index) +
               str(self.timestamp) +
               str(self.data) +
               str(self.previous_hash))
    return sha.hexdigest()

  @classmethod
  def genesis(cls):
    return cls(0, date.datetime.now(), {'proof-of-work': 9, 'transactions': None}, '0')

  @classmethod
  def pow(cls, last_proof):

    # Next proof of work
    incrementer = last_proof + 1

    # Keep incrementing the incrementer until it's equal to a number divisible by 9
    # and the proof of work of the previous block in the chain
    while not (incrementer % 9 == 0 and incrementer % last_proof == 0):
      incrementer += 1

    # Once that number is found we can return it as a proof of our work
    return incrementer

  def to_dict(self):
    return {
      'data': self.data,
      'hash': self.hash,
      'index': self.index,
      'timestamp': str(self.timestamp)
    }

  def to_json(self):
    return json.dumps(self.to_dict(), indent=4, sort_keys=True)

###
## NODE CONFIGURATION (NETWORK SIMULATION)
#

class Node(object):
  def __init__(self, address, blockchain, mining=True, network=list(), transactions=list()):
    self.address = address
    self.blockchain = blockchain
    self.mining = mining
    self.network = network
    self.transactions = transactions

  def consensus(self):
    """ Establish blockchain consensus across the network.
        If our chain isn't longest, then we store the longest chain.
    """
    longest_chain = self.blockchain
    peer_chains = get_peer_blockchains()
    for chain in peer_chains:
      if len(longest_chain) < len(chain):
        longest_chain = chain
    self.blockchain = longest_chain

  def to_dict(self):
    return {
      'address': self.address,
      'blockchain': map(lambda b: b.to_dict(), self.blockchain),
      'mining': self.mining,
      'network': self.network,
      'transactions': self.transactions
    }

  def to_json(self):
    return json.dumps(self.to_dict(), indent=4, sort_keys=True)

###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~
# Multi Node Network Simulation
network_dict = dict()
genesis_list = [Block.genesis()]
for n in range(1,21):
  node_address = 'node{:02}'.format(n)
  network_dict.update({
    node_address: Node(address=node_address, blockchain=genesis_list)
  })

network_keys = network_dict.keys()
network_keys.sort()
for node_address in network_keys:
  network_dict[node_address].network=network_keys

def get_node(network_node=None):
  """ return a specific node on the network
  """
  return network_dict.get(network_node or network_keys[-1])

def get_peer_blockchains():
  """ simulate network communication with peer nodes on the network
  """
  return map(lambda peer_node: map(lambda blockchain: blockchain.to_dict(), peer_node.blockchain), network_dict.values())

###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~###~

###
##  NODE ROUTING
#

@node.route('/mine/<node_key>', methods=['GET'])
def mine(node_key):
  # dynamic host node
  this_node = get_node(node_key)
  print(this_node.to_json())

  # Establish consensus with the network.
  this_node.consensus()

  # Get the last proof-of-work
  last_block = this_node.blockchain[-1]
  last_proof = last_block.data['proof-of-work']

  # Calculate proof of work for a new block
  proof = Block.pow(last_proof)

  # Reward the miner by adding a transaction
  this_node.transactions.append({
    'from': 'network',
    'to': this_node.address,
    'amount': 1
  })

  # Create a newly mined block
  mined_block = Block(
    index = last_block.index + 1,
    timestamp = date.datetime.now(),
    data = {
      'proof-of-work': proof,
      'transactions': list(this_node.transactions)
    },
    previous_hash = last_block.hash
  )

  # Add the mined block to our local chain
  this_node.blockchain.append(mined_block)

  # Clean up
  this_node.transactions = list()

  # Inform the client
  return """
<pre>{}</pre>
""".format(mined_block.to_json())

# Host it...
node.run()


@node.route('/txion', methods=['POST'])
def transaction():
  # Extract the transaction data
  new_txion = request.get_json()

  # Add the transaction to our list
  # TRANSACTIONS.append(new_txion)

  # Log the transaction to our console
  print "New transaction"
  print "From: {}".format(new_txion['from'].encode('ascii','replace'))
  print "To: {}".format(new_txion['to'].encode('ascii','replace'))
  print "AMOUNT: {}\n".format(new_txion['amount'])

  # Let the client know it worked out
  return "Transaction submission successful\n"

