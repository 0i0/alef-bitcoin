old.py
from decimal import *
from jsonrpc import ServiceProxy, json

def get_transaction_log():
  txs = {"inputs":
        [{ "txid":"6bf0c39118b0c22a40eec87fb82f8a2650aa425e5b77808d683e23023d685385", "vout":1,"privatekey":"cVhQoC4jtNPZ3Ct5Euxa9B7N7La7s5oPF1yLRgRJNYWLVpzmLjqi"}
        ,{ "txid":"6bf0c39118b0c22a40eec87fb82f8a2650aa425e5b77808d683e23023d685385", "vout":0,"privatekey":"cUzRiidJ2syK9RiW6mzEzfvMLXaAd34z9cFKS3CpiRR9cuHZLh7c"}
        
        ],
      "outputs":
        [{"toaddress":"muJvRoPVYv34YS8ZxCGiXaSGYEXTQkWzpW","amount":Decimal("45.0")}
        ]
        }
  return txs

def orginize_input_list(rawinputs):
  inputs = []
  for input in rawinputs:
    inputs.append({ "txid":input["txid"], "vout":input["vout"]})
  return inputs

def orginize_ouput_list(rawoutputs):
  outputs = {}
  for output in rawoutputs:
    outputs[output["toaddress"]] = float(output["amount"])
  return outputs

def get_privatekeys(rawinputs):
  privatekeys = []
  for input in rawinputs:
    privatekeys.append(input["privatekey"])
  print privatekeys
  return privatekeys

def create_tx(bitcoind, rawinputs,rawoutputs):
  inputs = orginize_input_list(rawinputs)
  outputs = orginize_ouput_list(rawoutputs)
  privatekeys = get_privatekeys(rawinputs)
  rawtx = bitcoind.createrawtransaction(inputs, outputs)
  signed_rawtx = bitcoind.signrawtransaction(rawtx, [], privatekeys)
  return signed_rawtx

def main():
  bitcoind = ServiceProxy("http://lior:lior1@127.0.0.1:8332")
  txs = get_transaction_log()
  txdata = create_tx(bitcoind, txs["inputs"],txs["outputs"])
  print txdata


if __name__ == '__main__':
    main()



# for info in bitcoind.listreceivedbyaddress(0):
#   print info["txids"][0]
#   txdata = bitcoind.getrawtransaction(info["txids"][0], 1)
#   decodedtx = bitcoind.decoderawtransaction(txdata["hex"])
#   print decodedtx