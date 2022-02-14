import Option
import OHLCV_Stream
import pandas as pd
import numpy as np


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


### BTCUSDT['st'], BTCUSDT['s_upt'], BTCUSDT['st_dt'] = get_supertrend(BTCUSDT['high'], BTCUSDT['low'], BTCUSDT['close'], 10, 3)
### BTCUSDT = BTCUSDT[1:]

#print(BTCUSDT.head())

# SUPERTREND PLOT

"""plt.plot(BTCUSDT['close'], linewidth=2, label='CLOSING PRICE')
plt.plot(BTCUSDT['st'], color='green', linewidth=2, label='ST UPTREND 10,3')
plt.plot(BTCUSDT['st_dt'], color='r', linewidth=2, label='ST DOWNTREND 10,3')
plt.legend(loc='upper left')
plt.show()"""


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


### buy_price, sell_price, st_signal = implement_st_strategy(BTCUSDT['close'], BTCUSDT['st'])

# SUPERTREND SIGNALS

#fig = plt.figure(num=1, figsize=(20, 10), dpi=100, facecolor='w', edgecolor='k')
#fig = fig.axes()
#candlestick2_ochl(fig, open_1h,close_1h,high_1h,low_1h, width=0.965, colorup='r', colordown='b', alpha=1)

"""plt.plot(BTCUSDT['close'], linewidth=2)
plt.plot(BTCUSDT['st'], color='green', linewidth=2, label='ST UPTREND')
plt.plot(BTCUSDT['st_dt'], color='red', linewidth=2, label='ST DOWNTREND')
plt.plot(BTCUSDT.index, buy_price, marker='^', color='green', markersize=12, linewidth=0, label='BUY SIGNAL')
plt.plot(BTCUSDT.index, sell_price, marker='v', color='r', markersize=12, linewidth=0, label='SELL SIGNAL')
plt.title('BTCUSDT ST TRADING SIGNALS')
plt.legend(loc='upper left')
plt.show()"""
# GENERATING STOCK POSITION
"""position = []
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

strategy.head()"""
#print(strategy[20:25])



def ST_stream(input_df):
    #global BTCUSDT
    BTCUSDT = input_df#OHLCV_Stream.BTCUSDT
    BTCUSDT['st'], BTCUSDT['s_upt'], BTCUSDT['st_dt'] = get_supertrend(BTCUSDT['high'], BTCUSDT['low'],BTCUSDT['close'], 10, 3)
    BTCUSDT = BTCUSDT[1:]

    buy_price, sell_price, st_signal = implement_st_strategy(BTCUSDT['close'], BTCUSDT['st'])

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

    return BTCUSDT, st_signal, position, buy_price, sell_price
