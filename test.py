from decimal import *
from jsonrpc import ServiceProxy, json
import copy

bitcoind = ServiceProxy("http://lior:lior1@127.0.0.1:8332")

unspent =  bitcoind.listunspent(0)
inputs = []
for tx in unspent:
  inputs.append({"txid":tx["txid"],"vout":tx["vout"],"privatekey":bitcoind.dumpprivkey(tx["address"])})

# print bitcoind.getnewaddress()


def get_transaction_log():
    txs =  [
                {"vin":
                    [{'privatekey': u'cTcpfmbWC6amaKCxAPN15177YLpSmnKNX3SCzmGkSnfb8bwznWMC', 'vout': 1, 'txid': u'4472d3edaeeba7d9feee129c073c6dfd0c8464d79eb215cc79a368abb61bc294'}, 
                    {'privatekey': u'cTcpfmbWC6amaKCxAPN15177YLpSmnKNX3SCzmGkSnfb8bwznWMC', 'vout': 1, 'txid': u'5aceeb2acec5e0d964a100975da5a3e641811fda8c23d7247f98f939dc50c7d8'}],
                "vout":
                    [{"toaddress":"mj6ViSZBzbQdRn37MdGTqTLYbn62sV4ztR","amount":Decimal("0.003")}
                    ,{"toaddress":"mj6ViSZBzbQdRn37MdGTqTLYbn62sV4ztR","amount":Decimal("0.004")}
                    ]
                },
                {"vin":
                    [{'privatekey': u'cTcpfmbWC6amaKCxAPN15177YLpSmnKNX3SCzmGkSnfb8bwznWMC', 'vout': 1, 'txid': u'4472d3edaeeba7d9feee129c073c6dfd0c8464d79eb215cc79a368abb61bc294'}, 
                    {'privatekey': u'cTcpfmbWC6amaKCxAPN15177YLpSmnKNX3SCzmGkSnfb8bwznWMC', 'vout': 1, 'txid': u'5aceeb2acec5e0d964a100975da5a3e641811fda8c23d7247f98f939dc50c7d8'}],
                "vout":
                    [{"toaddress":"mhJtJ711pAfUFsg7Qd9RkXZFcxPLNesgrz","amount":Decimal("0.002")}
                    ]
                },
            ]    
    return txs

def check_for_duplicate_input_output(tx,tx2):
  for base_input in tx["vin"]:
    for input in tx2["vin"]:
      if base_input["vout"]==input["vout"] and base_input["txid"]==input["txid"]:
        return True
  return False

def input_exist(tx,base_input):
  for input in tx["vin"]:
    if base_input["vout"]==input["vout"] and base_input["txid"]==input["txid"]:
      return True
  return False

def merge_two_txs(tx,tx2):
  for input in tx2["vin"]:
    if not input_exist(tx,input):
      tx["vin"].append(input)
  for output in tx2["vout"]:
    tx["vout"].append(output)
  return tx

def merge_tx(txs):
    merge_txs = []
    while len(txs)>0:
      base_tx = txs[0]
      txs.remove(base_tx)
      for tx in txs:
        if check_for_duplicate_input_output(base_tx,tx):
          base_tx = merge_two_txs(base_tx,tx)
          txs.remove(tx)
      merge_txs.append(base_tx)
    return merge_txs

txs = get_transaction_log()
merged_txs = merge_tx(txs)
print merged_txs    