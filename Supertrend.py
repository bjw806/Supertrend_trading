# IMPORTING PACKAGES
import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from math import floor
from termcolor import colored as cl
from mplfinance.original_flavor import candlestick2_ochl


plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)


# EXTRACTING DATA
binance_futures = ccxt.binance(config={
        'apiKey': '3vldXTBVRHRM9C3cXdWBvfa4wkyOaVFjbL91dpYfyYonXsoMraO1MXcrXaxZ8vSW',
        'secret': 'kPL3Gl06MRTZ6tfkwWTJN9ZXT5sEQhpyV9hE5kOL0cw4OgVTPO9WadYLOagQmWx3',
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}})

binance = ccxt.binance({'options': {'defaultType': 'future'}})
ticker = binance.fetch_ticker('BTC/USDT')
markets = binance_futures.load_markets()
market = binance_futures.market("BTC/USDT")

ohlcv_1h = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=300)

def get_historical_data(symbol, start_date):
    #api_key = YOUR
    #API
    #KEY
    #api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    #raw_df = requests.get(api_url).json()
    #df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    #df = df[df.index >= start_date]
    #df.index = pd.to_datetime(df.index)

    df = pd.DataFrame(ohlcv_1h, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    return df

BTCUSDT = get_historical_data('BTC/USDT', '2020-01-01')
#print(BTCUSDT)


################
open_1h, high_1h, low_1h, close_1h, volume_1h, date_1h, close_1h_pd = [], [], [], [], [], [], []
for x in range(6):
    open_1h.append(float(ohlcv_1h[x][1]))
    high_1h.append(float(ohlcv_1h[x][2]))
    low_1h.append(float(ohlcv_1h[x][3]))
    close_1h.append(float(ohlcv_1h[x][4]))
    volume_1h.append(float(ohlcv_1h[x][5]))
    date_1h.append(ohlcv_1h[x][0])
###################



# SUPERTREND CALCULATION
def get_supertrend(high, low, close, lookback, multiplier):
    # ATR

    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.ewm(lookback).mean()

    # H/L AVG AND BASIC UPPER & LOWER BAND

    hl_avg = (high + low) / 2
    upper_band = (hl_avg + multiplier * atr).dropna()
    lower_band = (hl_avg - multiplier * atr).dropna()

    # FINAL UPPER BAND

    final_bands = pd.DataFrame(columns=['upper', 'lower'])
    final_bands.iloc[:, 0] = [x for x in upper_band - upper_band]
    final_bands.iloc[:, 1] = final_bands.iloc[:, 0]

    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 0] = 0
        else:
            if (upper_band[i] < final_bands.iloc[i - 1, 0]) | (close[i - 1] > final_bands.iloc[i - 1, 0]):
                final_bands.iloc[i, 0] = upper_band[i]
            else:
                final_bands.iloc[i, 0] = final_bands.iloc[i - 1, 0]

    # FINAL LOWER BAND

    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 1] = 0
        else:
            if (lower_band[i] > final_bands.iloc[i - 1, 1]) | (close[i - 1] < final_bands.iloc[i - 1, 1]):
                final_bands.iloc[i, 1] = lower_band[i]
            else:
                final_bands.iloc[i, 1] = final_bands.iloc[i - 1, 1]

    # SUPERTREND

    supertrend = pd.DataFrame(columns=[f'supertrend_{lookback}'])
    supertrend.iloc[:, 0] = [x for x in final_bands['upper'] - final_bands['upper']]

    for i in range(len(supertrend)):
        if i == 0:
            supertrend.iloc[i, 0] = 0
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 0] and close[i] < final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 0] and close[i] > final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 1] and close[i] > final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 1] and close[i] < final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]

    supertrend = supertrend.set_index(upper_band.index)
    supertrend = supertrend.dropna()[1:]

    # ST UPTREND/DOWNTREND

    upt = []
    dt = []
    close = close.iloc[len(close) - len(supertrend):]

    for i in range(len(supertrend)):
        if close[i] > supertrend.iloc[i, 0]:
            upt.append(supertrend.iloc[i, 0])
            dt.append(np.nan)
        elif close[i] < supertrend.iloc[i, 0]:
            upt.append(np.nan)
            dt.append(supertrend.iloc[i, 0])
        else:
            upt.append(np.nan)
            dt.append(np.nan)

    st, upt, dt = pd.Series(supertrend.iloc[:, 0]), pd.Series(upt), pd.Series(dt)
    upt.index, dt.index = supertrend.index, supertrend.index

    return st, upt, dt


BTCUSDT['st'], BTCUSDT['s_upt'], BTCUSDT['st_dt'] = get_supertrend(BTCUSDT['high'], BTCUSDT['low'], BTCUSDT['close'], 10, 3)
BTCUSDT = BTCUSDT[1:]
print(BTCUSDT.head())

# SUPERTREND PLOT

plt.plot(BTCUSDT['close'], linewidth=2, label='CLOSING PRICE')
plt.plot(BTCUSDT['st'], color='green', linewidth=2, label='ST UPTREND 10,3')
plt.plot(BTCUSDT['st_dt'], color='r', linewidth=2, label='ST DOWNTREND 10,3')
plt.legend(loc='upper left')
plt.show()


# SUPERTREND STRATEGY

def implement_st_strategy(prices, st):
    buy_price = []
    sell_price = []
    st_signal = []
    signal = 0

    for i in range(len(st)):
        if st[i - 1] > prices[i - 1] and st[i] < prices[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                st_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                st_signal.append(0)
        elif st[i - 1] < prices[i - 1] and st[i] > prices[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                st_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                st_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            st_signal.append(0)

    return buy_price, sell_price, st_signal


buy_price, sell_price, st_signal = implement_st_strategy(BTCUSDT['close'], BTCUSDT['st'])

# SUPERTREND SIGNALS

#fig = plt.figure(num=1, figsize=(20, 10), dpi=100, facecolor='w', edgecolor='k')
#fig = fig.axes()
#candlestick2_ochl(fig, open_1h,close_1h,high_1h,low_1h, width=0.965, colorup='r', colordown='b', alpha=1)

plt.plot(BTCUSDT['close'], linewidth=2)
plt.plot(BTCUSDT['st'], color='green', linewidth=2, label='ST UPTREND')
plt.plot(BTCUSDT['st_dt'], color='red', linewidth=2, label='ST DOWNTREND')
plt.plot(BTCUSDT.index, buy_price, marker='^', color='green', markersize=12, linewidth=0, label='BUY SIGNAL')
plt.plot(BTCUSDT.index, sell_price, marker='v', color='r', markersize=12, linewidth=0, label='SELL SIGNAL')
plt.title('BTCUSDT ST TRADING SIGNALS')
plt.legend(loc='upper left')
plt.show()
# GENERATING STOCK POSITION
position = []
for i in range(len(st_signal)):
    if st_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)

for i in range(len(BTCUSDT['close'])):
    if st_signal[i] == 1:
        position[i] = 1
    elif st_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i - 1]

close_price = BTCUSDT['close']
st = BTCUSDT['st']
st_signal = pd.DataFrame(st_signal).rename(columns={0: 'st_signal'}).set_index(BTCUSDT.index)
position = pd.DataFrame(position).rename(columns={0: 'st_position'}).set_index(BTCUSDT.index)

frames = [close_price, st, st_signal, position]
strategy = pd.concat(frames, join='inner', axis=1)

strategy.head()
print(strategy[20:25])
# BACKTESTING
BTCUSDT_ret = pd.DataFrame(np.diff(BTCUSDT['close'])).rename(columns={0: 'returns'})
st_strategy_ret = []

for i in range(len(BTCUSDT_ret)):
    returns = BTCUSDT_ret['returns'][i] * strategy['st_position'][i]
    st_strategy_ret.append(returns)

st_strategy_ret_df = pd.DataFrame(st_strategy_ret).rename(columns={0: 'st_returns'})
investment_value = 100000
number_of_stocks = floor(investment_value / BTCUSDT['close'][-1])
st_investment_ret = []

for i in range(len(st_strategy_ret_df['st_returns'])):
    returns = number_of_stocks * st_strategy_ret_df['st_returns'][i]
    st_investment_ret.append(returns)

st_investment_ret_df = pd.DataFrame(st_investment_ret).rename(columns={0: 'investment_returns'})
total_investment_ret = round(sum(st_investment_ret_df['investment_returns']), 2)
profit_percentage = floor((total_investment_ret / investment_value) * 100)
print(cl('Profit gained from the ST strategy by investing $100k in BTCUSDT : {}'.format(total_investment_ret),
         attrs=['bold']))
print(cl('Profit percentage of the ST strategy : {}%'.format(profit_percentage), attrs=['bold']))


# SPY ETF COMPARISON
"""def get_benchmark(start_date, investment_value):
    spy = get_historical_data('SPY', start_date)['close']
    benchmark = pd.DataFrame(np.diff(spy)).rename(columns={0: 'benchmark_returns'})

    investment_value = investment_value
    number_of_stocks = floor(investment_value / spy[-1])
    benchmark_investment_ret = []

    for i in range(len(benchmark['benchmark_returns'])):
        returns = number_of_stocks * benchmark['benchmark_returns'][i]
        benchmark_investment_ret.append(returns)

    benchmark_investment_ret_df = pd.DataFrame(benchmark_investment_ret).rename(columns={0: 'investment_returns'})
    return benchmark_investment_ret_df


benchmark = get_benchmark('2020-01-01', 100000)
investment_value = 100000
total_benchmark_investment_ret = round(sum(benchmark['investment_returns']), 2)
benchmark_profit_percentage = floor((total_benchmark_investment_ret / investment_value) * 100)
print(cl('Benchmark profit by investing $100k : {}'.format(total_benchmark_investment_ret), attrs=['bold']))
print(cl('Benchmark Profit percentage : {}%'.format(benchmark_profit_percentage), attrs=['bold']))
print(cl('ST Strategy profit is {}% higher than the Benchmark Profit'.format(
    profit_percentage - benchmark_profit_percentage), attrs=['bold']))"""