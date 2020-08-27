#!/usr/bin/env python3
"""
Monitor Zyxel modem.

login sequence:
Request URL: http://192.168.0.1/login.cgi
Request Method: POST
admin_username: admin
"""

import sys
import os.path
import configparser
import time
import requests
from requests_file import FileAdapter
from bs4 import BeautifulSoup, SoupStrainer


class Unbuffered(object):
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


def main():
    sys.stdout = Unbuffered(sys.stdout)

    config_file = os.path.join(os.path.expanduser("~"), '.config', 'monitor_bw', 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_file)

    admin_username = config['DEFAULT']['admin_username']
    admin_password = config['DEFAULT']['admin_password']

    loginurl = "http://192.168.0.1/login.cgi"

    s = requests.Session()
    s.post(loginurl, data={'admin_username': admin_username, 'admin_password': admin_password})

    dslRxByteTotal = 30
    dslTxByte1Total = 31

    # session_cookie = "227541000"
    # session_cookie = "317453000"
    #session_cookie = "718106000"
    # s = requests.Session()
    #s.cookies.set('SESSION', session_cookie)

    while True:
        staturl = "http://192.168.0.1/GetDslStatus.html"
        # staturl = "http://192.168.0.1/GetDslStatus2.html"

        content = s.get(staturl)
        # print(content)
        dslstats = content.text.split('||')
        # print(dslstats)
        print(dslstats[dslRxByteTotal], dslstats[dslTxByte1Total])
        sys.stdout.flush()
        time.sleep(10)


if __name__ == "__main__":
    main()
