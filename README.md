# monitor_bw
Monitor bandwidth of Zyxel C3000Z broadband modem, E.g. from CenturyLink

## Installation
Collecting data requires the `requests` module.

Tested on Ubuntu Linux 18.04

Copy the `config.ini-example` file to `$HOME/.config/monitor_bw/config.init`

Change the `admin-password` there to the password on your modem.

If necessary, administer it by hand by logging in to the modem via the web at

    http://192.168.0.1/

to set up your admin password and understand some of the data pulled here, etc.

Then run

    ./monitor_bw.py >> monitor.csv &

It will collect data every few seconds (as determined by the sleep() call) into a csv file.

After gathering some data, you can run the included Jupyter notebook to play with it.
