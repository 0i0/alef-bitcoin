from decimal import *
from jsonrpc import ServiceProxy, json

bitcoind = ServiceProxy("http://lior:lior1@127.0.0.1:8332")

unspent =  bitcoind.listunspent(0)
inputs = []
for tx in unspent:
  inputs.append({"txid":tx["txid"],"vout":tx["vout"],"privatekey":bitcoind.dumpprivkey(tx["address"])})
print inputs

print bitcoind.getnewaddress()