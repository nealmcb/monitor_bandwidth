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
from requests_file import FileAdapter
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime


class Unbuffered(object):
    "From Seb: https://stackoverflow.com/a/107717/507544"

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
    def __init__(self, url):
        self.url = url
        self.timestamp = None
        self.rxbw = None

    def new_session(self):
        "returns a new logged-in requests session"

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
        "update dslstats using given session"

        dslRxByteTotal = 30
        dslTxByte1Total = 31

        r = s.get(self.url)
        if r.status_code != 200  or  "||" not in r.text:
            s = self.new_session()
            r = s.get(self.url)
        # print(content)

        dslstats = r.text.split('||')

        timestamp = datetime.now()

        rx_total = float(dslstats[dslRxByteTotal])
        tx_total = float(dslstats[dslTxByte1Total])

        if self.timestamp:
            self.rxbw = (rx_total - self.lastrx) / (timestamp - self.timestamp).seconds
            #print(self.rxbw)

        self.timestamp = timestamp
        self.lastrx = rx_total
        self.lasttx = tx_total

        # print(dslstats)

        return s


class Modem:
    def __init__(self, dslurl1, dslurl2):
        self.s = requests.Session()
        self.dsl1 = DSL(dslurl1)
        self.dsl2 = DSL(dslurl2)


    def monitor(self):

        while True:
            self.s = self.dsl1.get_dsl_stats(self.s)
            self.s = self.dsl2.get_dsl_stats(self.s)

            ts = datetime.isoformat(self.dsl1.timestamp)
            print(f"{ts},{self.dsl1.rxbw},{self.dsl1.lastrx},{self.dsl1.lasttx},{self.dsl2.lastrx},{self.dsl2.lasttx}")

            time.sleep(10)


if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)

    modem = Modem("http://192.168.0.1/GetDslStatus.html", "http://192.168.0.1/GetDslStatus2.html")
    modem.monitor()
