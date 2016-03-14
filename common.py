import json
import requests
import sys

regtest = True
debug = True
allow_big_fee = False
amount_to_receive = 30
amount_to_send_offline_to_online = 20
default_tx_fee = 0.0002


def request(url, payload):
    resp = requests.post(
        url, data=json.dumps(payload), headers={'content-type': 'application/json'}
    ).json()

    if resp["error"] is not None:
        print "ERROR!!!"
        print payload
        print resp["error"]
        sys.exit(1)

    return resp


# a qrcode image can have more than just a qrcode (ie EAN-13)
# so lets make sure we just grab what we want
def get_qrcode_val_from_str(s):
    codes = s.split('\n')
    key = "a"
    i = 0
    while key != "QR-Code":
        key = codes[i].split(":")[0]
        val = codes[i].split(":")[1]
        i += 1

    return val
