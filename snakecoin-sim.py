""" SNAKE COIN MULTI-NODE SERVER
    Based on Gerald Nash's "Let's Make the Tiniest Blockchain Bigger"
    https://medium.com/crypto-currently/lets-make-the-tiniest-blockchain-bigger-ac360a328f4d
    https://gist.github.com/aunyks/47d157f8bc7d1829a729c2a6a919c173

    Adapted to my own style preferences.
    Added simulated multi-node support.
"""
import json
import random
import urllib2

node_key_list = json.loads(urllib2.urlopen('http://127.0.0.1:5000/node_keys').read())


for i in range(20):
  node_key = node_key_list[random.randint(0,len(node_key_list)-1)]
  print('===~===~===~===~===~===~===~===~===~===~===~===~===~===~===~===~==={}'.format(node_key))
  print(urllib2.urlopen('http://127.0.0.1:5000/mine/{}'.format(node_key)).read())

for node_key in node_key_list:
  print('===~===~===~===~===~===~===~===~===~===~===~===~===~===~===~===~==={}'.format(node_key))
  blockchain = json.loads(urllib2.urlopen('http://127.0.0.1:5000/chains/{}'.format(node_key)).read())
  print('length of chain: {}'.format(len(blockchain)))
