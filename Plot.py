import Calculate_ST
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick2_ochl
from mplfinance.original_flavor import candlestick_ohlc
import OHLCV_Stream
import Option
import matplotlib.dates as mpl_dates
import talib
import numpy as np

def ploting(ST_BTCUSDT,buy_price,sell_price):
    BTCUSDT = ST_BTCUSDT#Calculate_ST.BTCUSDT
    #st_siganl,st_position,buy_price,sell_price = Calculate_ST.ST_stream()
    #buy_price = Calculate_ST.buy_price
    #sell_price = Calculate_ST.sell_price

    plt.style.use('fivethirtyeight')
    plt.rcParams['figure.figsize'] = (20, 10)

    # fig = plt.figure(num=1, figsize=(20, 10), dpi=100, facecolor='w', edgecolor='k') # figsize: ppi dpi: 해상도
    # ax = fig.add_subplot(1,1,1)
    MA_25_1h = talib.MA(BTCUSDT['close'], timeperiod=25)

    plt.plot(BTCUSDT['close'], linewidth=2)
    plt.plot(MA_25_1h,linewidth=2)
    plt.plot(BTCUSDT['st'], color='green', linewidth=2, label='ST UPTREND')
    plt.plot(BTCUSDT['st_dt'], color='red', linewidth=2, label='ST DOWNTREND')
    plt.plot(BTCUSDT.index, buy_price, marker='^', color='green', markersize=12, linewidth=0, label='BUY SIGNAL')
    plt.plot(BTCUSDT.index, sell_price, marker='v', color='red', markersize=12, linewidth=0, label='SELL SIGNAL')
    plt.title('BTC/USDT ST TRADING SIGNALS')
    plt.legend(loc='upper left')
    plt.show()


#print(Calculate_ST.position[60:90])
#siganl
# -1 =  숏
# 1 = 롱
# 0 = NO ACTION