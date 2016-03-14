import common
import common_online
import json
import qrcode
from subprocess import Popen, PIPE


# this sends amt_to_send to addr_to_send.
# the offline balance minus tx_fee is sent to addr_to_save, which is the offline address
# if a tx fee can not be estimated, common.default_tx_fee is used
def create_raw_tx(backing_transaction, addr_to_send, amt_to_send, addr_to_save):
    est_tx_fee = common.request(common_online.on_url, {'method': 'estimatefee', 'params': [6]})

    tx_fee_per_kb = est_tx_fee['result']
    if common.debug:
        print "tx_fee: " + str(tx_fee_per_kb)
        print "backing_tx: " + str(backing_transaction)

    addrs_amts = {addr_to_send: amt_to_send,
                  addr_to_save: common.amount_to_receive - amt_to_send - common.default_tx_fee}
    create_raw_tx_est = common.request(common_online.on_url,
                                     {'method': 'createrawtransaction','params': [backing_transaction, addrs_amts]})

    if tx_fee_per_kb < 0:
        if common.debug:
            print "UNABLE to get tx fee"
        return create_raw_tx_est["result"]

    est_tx_size_kb = len(create_raw_tx_est["result"]) / 1000.0
    tx_fee = est_tx_size_kb * tx_fee_per_kb
    amt_to_save = amt_to_send - tx_fee
    addrs_amts = {addr_to_send: amt_to_send, addr_to_save: amt_to_save}
    create_raw_tx = common.request(common_online.on_url, {'method': 'createrawtransaction',
                                                        'params': [backing_transaction, addrs_amts]})
    raw_tx = create_raw_tx["result"]

    if common.debug:
        print "CREATED RAW TX:" + raw_tx

    return raw_tx


def main():
    if common.debug:
        print "BEGIN online_create_tx"

    qr_code_address1 = Popen(["zbarimg", "--quiet", "images/offline_address1.png"], stdout=PIPE).stdout.read()
    address_to_receive = common.get_qrcode_val_from_str(qr_code_address1)
    qr_code_address2 = Popen(["zbarimg", "--quiet", "images/offline_address2.png"], stdout=PIPE).stdout.read()
    address_to_save = common.get_qrcode_val_from_str(qr_code_address2)

    if common.debug:
        print "offline address1 read from qrcode: " + address_to_receive
        print "offline address2 read from qrcode: " + address_to_save

    if common.regtest:
        generating = common.request(common_online.on_url, {'method': 'generate', 'params': [ 101 ]})
        print generating["result"]

    send_to_offline_address = common.request(common_online.on_url,
                                             {'method': 'sendtoaddress',
                                              'params': [address_to_receive, common.amount_to_receive]})
    online_payment_txid = send_to_offline_address["result"]

    if common.debug:
        print "sent " + str(common.amount_to_receive) + " to " + address_to_receive
        print "txid: " + online_payment_txid

    online_getrawtx_response = common.request(common_online.on_url,
                                              {'method': 'getrawtransaction','params': [online_payment_txid, 1]})
    if common.debug:
        print "raw transaction as json:"
        print json.dumps(online_getrawtx_response, sort_keys=True, indent=4)

    vouts = online_getrawtx_response["result"]["vout"]
    amt = -1
    i = 0

    while amt != common.amount_to_receive:
        value = vouts[i]["value"]
        amt = value
        i += 1

    vout = vouts[i - 1]["n"]
    script_pub_key = vouts[i - 1]["scriptPubKey"]["hex"]

    if common.debug:
        print "vout: " + str(vout)
        print "script_pub_key: " + script_pub_key

    online_get_new_address = common.request(common_online.on_url, {'method': 'getnewaddress'})
    online_new_address = online_get_new_address["result"]
    if common.debug:
        print "online new address: " + online_new_address

    backing_tx = [{"txid": online_payment_txid, "vout": vout}]

    online_create_raw_tx = create_raw_tx(backing_tx,
                                         online_new_address,
                                         common.amount_to_send_offline_to_online,
                                         address_to_save)

    qrcode.make(online_create_raw_tx + "," +
                online_payment_txid + "," +
                str(vout) + "," +
                script_pub_key).save("images/raw_tx_to_sign.png")

    if common.debug:
        print "online_create_raw_tx" + str(online_create_raw_tx)
        print "END online_create_tx"

if __name__ == "__main__":
    main()
