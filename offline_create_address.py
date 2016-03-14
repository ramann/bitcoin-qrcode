import common
import common_offline
import qrcode


def main():
    if common.debug:
        print "BEGIN offline_create_address"

    offline_address1 = common.request(common_offline.off_url, {'method': 'getnewaddress'})["result"]
    qrcode.make(offline_address1).save("images/offline_address1.png")
    offline_address2 = common.request(common_offline.off_url, {'method': 'getnewaddress'})["result"]
    qrcode.make(offline_address2).save("images/offline_address2.png")

    if common.debug:
        print "offline address1: " + offline_address1
        print "offline address2: " + offline_address2
        print "offline addresses saved to qrcode"
        print "END offline_create_address"

if __name__ == "__main__":
    main()
