
from decimal import *
from jsonrpc import ServiceProxy, json

def get_transaction_log():
    txs =   [
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

def compute_amount_in(bitcoind, txinfo):
    result = Decimal("0.0")
    for vin in txinfo['vin']:
        in_info = bitcoind.getrawtransaction(vin['txid'], 1)
        vout = in_info['vout'][vin['vout']]
        result = result + vout['value']
    print("total in %f"%(result))
    return result

def compute_amount_out(txinfo):
    result = Decimal("0.0")
    for vout in txinfo['vout']:
        result = result + vout['amount']
    print("total out %f"%(result))
    return result

def get_change_address(bitcoind,txinfo):
    in_info = bitcoind.getrawtransaction(txinfo["vin"][0]['txid'], 1)
    vout = in_info['vout'][txinfo["vin"][0]['vout']]
    change_address = vout["scriptPubKey"]["addresses"][0]
    return change_address

def add_tx_change(bitcoind,txs):
    for tx in txs:
        total_input = compute_amount_in(bitcoind,tx)
        total_output = compute_amount_out(tx)
        change_address = get_change_address(bitcoind,tx)
        tx["change"] = {"toaddress":change_address,"amount": total_input-total_output}
    return txs

def get_privatekeys(txs):
  privatekeys = []
  for tx in txs:
    for input in tx["vin"]:
        privatekeys.append(input["privatekey"])
  print privatekeys
  return privatekeys

def orginize_input_list(txs):
    inputs = []
    for tx in txs:
        for input in tx["vin"]:
            inputs.append({ "txid":input["txid"], "vout":input["vout"]})
    return inputs

def orginize_ouput_list(txs):
    outputs = {}
    for tx in txs:
        for output in tx["vout"]:
            if output["toaddress"] in outputs:
                outputs[output["toaddress"]] += float(output["amount"])
            else:
                outputs[output["toaddress"]] = float(output["amount"])
        if tx["change"]["toaddress"] in outputs:     
            outputs[tx["change"]["toaddress"]] += float(tx["change"]["amount"])
        else:
            outputs[tx["change"]["toaddress"]] = float(tx["change"]["amount"])
    print outputs
    return outputs

def create_tx(bitcoind,agregated_txs):
    inputs = orginize_input_list(agregated_txs)
    outputs = orginize_ouput_list(agregated_txs)
    rawtx = bitcoind.createrawtransaction(inputs, outputs)
    return rawtx

def aggregate_txs_for_max_tx(bitcoind,txs):
    tx_size = 0
    agregated_txs = []
    max_size = 410
    n=0
    while tx_size < max_size and n<len(txs):
        last_tx_size = tx_size
        agregated_txs.append(txs[n])
        txdata = create_tx(bitcoind,agregated_txs)
        tx_size = len(txdata)/2
        n+=1
    if tx_size > max_size:
        return (agregated_txs.pop(len(agregated_txs)-1),last_tx_size)
    else:
        return (agregated_txs,tx_size)

def calculate_total_fees(tx_size):
    kb = tx_size/1000
    return (kb+1)*Decimal("0.0001")

def remove_needed_change(tx_size,agregated_txs):
    total_fees = calculate_total_fees(tx_size)
    fees_collected=0
    n=0
    while total_fees > fees_collected:
        fees_left_to_collect = total_fees - fees_collected
        if agregated_txs[n]["change"]["amount"] < fees_left_to_collect:
            fees_collected += agregated_txs[n]["change"]["amount"]
            agregated_txs[n]["change"]["amount"] = Decimal("0.0")
        else:
            print "taking fee"
            fees_collected += fees_left_to_collect
            agregated_txs[n]["change"]["amount"] -= Decimal(fees_left_to_collect)
        n+=1
    return agregated_txs

def main():
    bitcoind = ServiceProxy("http://lior:lior1@127.0.0.1:8332")
    txs = get_transaction_log()
    merged_txs = merge_tx(txs)
    txs_with_change = add_tx_change(bitcoind,merged_txs)
    # print bitcoind.decoderawtransaction(create_tx(bitcoind,txs_with_change))
    agregated_txs , tx_size = aggregate_txs_for_max_tx(bitcoind,txs_with_change)
    txs_after_fee = remove_needed_change(tx_size,agregated_txs)
    txdata = create_tx(bitcoind,txs_after_fee)
    privatekeys = get_privatekeys(txs_after_fee)
    signed_rawtx = bitcoind.signrawtransaction(txdata, [], privatekeys)
    print signed_rawtx["complete"]
    print bitcoind.decoderawtransaction(signed_rawtx["hex"])

if __name__ == '__main__':
    main()