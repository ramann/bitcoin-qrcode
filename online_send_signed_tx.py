import common
import common_online
from subprocess import Popen, PIPE


def main():

    if common.debug:
        print "BEGIN online_send_signed_tx"

    qrcode_signed_tx = Popen(["zbarimg", "--quiet", "images/offline_signed_tx.png"], stdout=PIPE).stdout.read()
    signed_tx = common.get_qrcode_val_from_str(qrcode_signed_tx)

    if common.debug:
        print "Loaded signed tx from qrcode:" + signed_tx

    online_send_raw_tx = common.request(common_online.on_url, {'method': 'sendrawtransaction',
                                                             'params': [signed_tx, common.allow_big_fee]})

    if common.debug:
        print "Sent raw tx: " + str(online_send_raw_tx)
        online_balance = common.request(common_online.on_url, {'method': 'getbalance', 'params': []})
        print "online_balance: "+str(online_balance['result'])
        print "END online_send_signed_tx"

if __name__ == "__main__":
    main()
