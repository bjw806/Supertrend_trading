# 옵션 세팅
import matplotlib.pyplot as plt
#import mpl_finance
import numpy
from matplotlib.gridspec import GridSpec
import talib
import ccxt
import time as TIME
import datetime
import pprint
import sys, os
import pandas as pd

numpy.set_printoptions(precision=6, suppress=True)

binance_futures = ccxt.binance(config={
        'apiKey': 'api-key',
        'secret': 'secret-key',
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}})

binance = ccxt.binance({'options': {'defaultType': 'future'}})
ticker = binance.fetch_ticker('BTC/USDT')
markets = binance_futures.load_markets()
market = binance_futures.market("BTC/USDT")


date_limit = 72
ohlcv_1h = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=date_limit)
ohlcv_add = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=1)

#leverage = 10 #x배
#resp = binance_futures.set_leverage("BTC/USDT",int(leverage))
###
my_position = 'n/a'
assets = 0
input_margin = 0
ROE = 0
total_profit = 0
PNL = 0
###
have_position = False
trade_amount = 0.03
fee = 1
win_count = 0
lose_count = 0
winrate = 0
###
stop_loss = -10
take_profit = 10
###

