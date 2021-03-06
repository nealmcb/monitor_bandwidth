#!/usr/bin/env python3
"""
Monitor Zyxel modem.

login sequence:
Request URL: http://192.168.0.1/login.cgi
Request Method: POST
admin_username: admin
admin_password: <pw>
"""

import sys
import os.path
import configparser
import time
import requests
from datetime import datetime


class Unbuffered(object):
    "Used to produce unbuffered output. From Seb: https://stackoverflow.com/a/107717/507544"

    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class DSL:
    "Represent one of the two bonded DSL lines used by the Zyxel"

    def __init__(self, url):
        self.url = url
        self.timestamp = None
        self.rxbw = 0.0
        self.txbw = 0.0

    def new_session(self):
        "Returns a new logged-in requests session"

        config_file = os.path.join(os.path.expanduser("~"), '.config', 'monitor_bw', 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_file)

        admin_username = config['DEFAULT']['admin_username']
        admin_password = config['DEFAULT']['admin_password']

        loginurl = "http://192.168.0.1/login.cgi"

        s = requests.Session()
        r = s.post(loginurl, data={'admin_username': admin_username, 'admin_password': admin_password})
        assert r.status_code == 200, f"Failed login at {loginurl}: {r}"

        return s

    def get_dsl_stats(self, s):
        "Capture and calculate latest data using given session"

        dslRxByteTotal = 30
        dslTxByte1Total = 31

        r = s.get(self.url)
        if r.status_code != 200  or  "||" not in r.text:
            s = self.new_session()
            r = s.get(self.url)

        dslstats = r.text.split('||')

        timestamp = datetime.now()

        rx_total = float(dslstats[dslRxByteTotal])
        tx_total = float(dslstats[dslTxByte1Total])

        if self.timestamp:
            dt = (timestamp - self.timestamp).seconds

            self.rxbw = (rx_total - self.lastrx) / dt
            self.txbw = (tx_total - self.lasttx) / dt

        self.timestamp = timestamp
        self.lastrx = rx_total
        self.lasttx = tx_total

        # print(dslstats)

        return s


class Modem:
    "A Zyzel C3000Z *broadband modem"

    def __init__(self, dslurl1, dslurl2):
        self.s = requests.Session()
        self.dsl1 = DSL(dslurl1)
        self.dsl2 = DSL(dslurl2)


    def monitor(self):

        print("ts,dsl1_rxbw,dsl2_rxbw,dsl1_txbw,dsl2_txbw,dsl1_lastrx,dsl2_lastrx,dsl1_lasttx,dsl2_lasttx")

        while True:
            self.s = self.dsl1.get_dsl_stats(self.s)
            self.s = self.dsl2.get_dsl_stats(self.s)

            ts = datetime.isoformat(self.dsl1.timestamp)
            print(f"{ts},{self.dsl1.rxbw:.5f},{self.dsl2.rxbw:.5f},{self.dsl1.txbw:.5f},{self.dsl2.txbw:.5f},{self.dsl1.lastrx},{self.dsl2.lastrx},{self.dsl1.lasttx},{self.dsl2.lasttx}")

            time.sleep(7)  # include a few seconds for taking data
            #time.sleep(97)  # include a few seconds for taking data


if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)

    modem = Modem("http://192.168.0.1/GetDslStatus.html", "http://192.168.0.1/GetDslStatus2.html")
    modem.monitor()
