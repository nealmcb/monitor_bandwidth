#!/usr/bin/env python3
"Read data from stdin the format produced by monitor_bw.py, and save a plot"

import sys
import csv
import matplotlib.pyplot as plt
import pandas as pd

def saveplot():
    plt.rcParams['figure.figsize'] = 13, 8

    df = pd.read_csv(sys.stdin, parse_dates=['ts'])
    df.set_index('ts', inplace=True)

    plot = df[['dsl1_rxbw', 'dsl1_txbw']].plot()
    fig = plot.get_figure()
    fig.savefig("monitor.png", dpi=130.)


if __name__ == "__main__":
    saveplot()
