import sys
import common
import common_offline
import qrcode
from subprocess import Popen, PIPE


def main():

    if common.debug:
        print "BEGIN offline_sign_tx"

    qrcode_tx_to_sign = Popen(["zbarimg", "--quiet", "images/raw_tx_to_sign.png"], stdout=PIPE).stdout.read()
    tx_to_sign = common.get_qrcode_val_from_str(qrcode_tx_to_sign).split(",")

    unspent_tx_output_details = [{"txid": str(tx_to_sign[1]),
                                  "vout": int(tx_to_sign[2]),
                                  "scriptPubKey": str(tx_to_sign[3])}]

    if common.debug:
        print "raw tx data read from qrcode"

    offline_sign_raw_tx = common.request(common_offline.off_url,
                                         {'method': 'signrawtransaction',
                                        'params': [tx_to_sign[0], unspent_tx_output_details]})

    if not offline_sign_raw_tx["result"]["complete"]:
        print "ERROR! tx signing incomplete!"
        print offline_sign_raw_tx
        sys.exit(1)

    if common.debug:
        print "signed tx offline: " + str(offline_sign_raw_tx)

    qrcode.make(offline_sign_raw_tx["result"]["hex"]).save('images/offline_signed_tx.png')

    if common.debug:
        print "signed offline transaction and saved qrcode: offline_signed_tx.png"
        print "END offline_sign_tx"

if __name__ == "__main__":
    main()
