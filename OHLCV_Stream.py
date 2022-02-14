import Option
import pandas as pd
import time as TIME
import datetime

def get_historical_data(input):
    if(input == None):
        df = pd.DataFrame(Option.ohlcv_1h, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    else:
        df = pd.DataFrame(input, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    return df

#1시간 단위로 add/delete 해주고 나머지는 갱신만. (최하위 행 삭제후 추가)
def add_data(old_df,replace_df):#like a queue Option.ohlcv_add
    df = pd.DataFrame(replace_df, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    df = pd.concat([old_df.iloc[1:],df])
    return df

def replace_data(old_df,replace_df):#like a stack Option.ohlcv_add
    df = pd.DataFrame(replace_df, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    df = pd.concat([old_df.iloc[:-1], df])
    return df

def chart_stream(input_data):
    date = datetime.datetime.now()
    time = date.strftime('%H:%M:%S')
    sec = (str(time).split(':'))[2]
    min = (str(time).split(':'))[1]

    if ((min == '59') and sec == '57'):
        print("add")
        add_data(input_data)

    if (min != '59' and sec == '57'):
        print("replace")
        replace_data(input_data)

    TIME.sleep(1)
    return 0



BTCUSDT = get_historical_data(None)

"""###
ohlcv_1h = Option.ohlcv_1h
open_1h, high_1h, low_1h, close_1h, volume_1h, date_1h, close_1h_pd = [], [], [], [], [], [], []
for x in range(Option.date_limit):
    open_1h.append(float(ohlcv_1h[x][1]))
    high_1h.append(float(ohlcv_1h[x][2]))
    low_1h.append(float(ohlcv_1h[x][3]))
    close_1h.append(float(ohlcv_1h[x][4]))
    volume_1h.append(float(ohlcv_1h[x][5]))
    date_1h.append(ohlcv_1h[x][0])"""