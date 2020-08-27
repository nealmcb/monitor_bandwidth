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


def new_session():
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


def get_dsl_stats(s, url):
    "return dslstats from given url"

    r = s.get(url)
    if r.status_code != 200  or  "||" not in r.text:
        s = new_session()
        r = s.get(staturl)
    # print(content)
    dslstats = r.text.split('||')
    # print(dslstats)



def monitor():
    sys.stdout = Unbuffered(sys.stdout)

    dslRxByteTotal = 30
    dslTxByte1Total = 31

    s = new_session()

    lasttx = {}
    lastrx = {}

    while True:
      for staturl in ["http://192.168.0.1/GetDslStatus.html", "http://192.168.0.1/GetDslStatus2.html"]:

        r = s.get(staturl)
        if r.status_code != 200  or  "||" not in r.text:
            s = new_session()
            r = s.get(staturl)
        # print(content)
        dslstats = r.text.split('||')
        # print(dslstats)
        timestamp = datetime.isoformat(datetime.now())

        timestamp = datetime.isoformat(datetime.now())

        lastrx[staturl] = dslstats[dslRxByteTotal]
        lasttx[staturl] = dslstats[dslTxByte1Total]

        #timestamp},{dslstats[dslRxByteTotal]},{}")

        print(f"{timestamp},{dslstats[dslRxByteTotal]},{dslstats[dslTxByte1Total]}")

      time.sleep(10)


if __name__ == "__main__":
    monitor()
