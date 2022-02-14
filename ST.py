import pandas_ta as ta
import OHLCV_Stream
import pandas as pd
import time as TIME
import datetime
import sys
import telegram_bot
import ccxt
import talib

#pd.set_option('display.max_columns',None)
#pd.set_option('display.max_rows',None)

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
def fetch_72h():
    ohlcv_1h = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=date_limit)
    return ohlcv_1h
def fetch_1h():
    ohlcv_add = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=1)
    return ohlcv_add
def fetch_15m(date):
    ohlcv = binance.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=date)
    return ohlcv
def fetch_5m(date):
    ohlcv = binance.fetch_ohlcv('BTC/USDT', timeframe='5m', limit=date)
    return ohlcv
def fetch_1m(date):
    ohlcv = binance.fetch_ohlcv('BTC/USDT', timeframe='1m', limit=date)
    return ohlcv

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
ST = 'n/a'

def open_long_position():
    global my_position
    my_position = 'long'
    print('[Long Open]')
    """order = binance_futures.create_market_buy_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Long", "Open", trade_amount, 0, total_profit)"""
    telegram_bot.send_trading_message(1, 1, "Long", "Open", trade_amount, 0, total_profit)
    #pprint.pprint(order)

def open_short_position():
    global my_position
    my_position = 'short'
    print('[Short Open]')
    """order = binance_futures.create_market_sell_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Short", "Open", trade_amount, 0, total_profit)"""
    telegram_bot.send_trading_message(1, 1, "Short", "Open", trade_amount, 0, total_profit)
    #pprint.pprint(order)

def close_long_position():
    global total_profit
    global win_count
    global lose_count
    global winrate
    global my_position
    my_position = 'n/a'
    print('[Long Close]')
    print('PNL:',PNL,'USDT')
    print('ROE:',ROE,'%')
    #re_info()
    total_profit += PNL
    if(PNL > 0):
        win_count += 1
    else:
        lose_count += 1
    if((win_count+lose_count) != 0):
        winrate = win_count / (win_count + lose_count)*100
    """order = binance_futures.create_market_sell_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Long", "Close", trade_amount, PNL, total_profit)"""
    telegram_bot.send_trading_message(1, 1, "Long", "Close", trade_amount, PNL, total_profit)
    #pprint.pprint(order)

def close_short_position():
    global total_profit
    global win_count
    global lose_count
    global winrate
    global my_position
    my_position = 'n/a'
    print('[Short Close]')
    print('PNL:', PNL, 'USDT')
    print('ROE:', ROE, '%')
    #re_info()
    total_profit += PNL
    if(PNL > 0):
        win_count += 1
    else:
        lose_count += 1
    if((win_count+lose_count) != 0):
        winrate = win_count / (win_count + lose_count)*100
    """order = binance_futures.create_market_buy_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Short", "Close", trade_amount, PNL, total_profit)"""
    telegram_bot.send_trading_message(1, 1, "Short", "Close", trade_amount, PNL, total_profit)
    #pprint.pprint(order)

def re_info():
    global PNL
    global have_position
    global assets
    global my_position
    global input_margin
    global ROE

    balance = binance_futures.fetch_balance()
    assets = (binance_futures.fetch_balance(params={"type": "future"}))['USDT']
    positions = balance['info']['positions']
    for position in positions:
        if position["symbol"] == "BTCUSDT":
            PNL = float(position["unrealizedProfit"])
            if(float(position["positionAmt"]) == trade_amount):
                have_position = True
                my_position = 'long'
            elif(float(position["positionAmt"]) == -trade_amount):
                have_position = True
                my_position = 'short'
            else:
                have_position = False
                my_position = 'n/a'
        input_margin = float(assets["used"])
    if(have_position):
        ROE = PNL/input_margin*100
    else:
        ROE = 0

def print_my_info():
    print("\r\n==========| My Info |==========")
    print("Assets:", assets)
    print("Input Margin:", input_margin)
    print("My Position:", my_position)
    print("Total_profit:", total_profit,"USDT")
    print("PNL:", PNL,"USDT")
    print("ROE:", ROE)
    print("Wins:", win_count)
    print("Loses:", lose_count)
    print("Winrate:", winrate,"%")

def close_my_position():
    if(my_position == 'long'):
        close_long_position()
    elif(my_position == 'short'):
        close_short_position()
    else:
        print("[No Position]")
#df = OHLCV_Stream.get_historical_data()
#sti = ta.supertrend(BTCUSDT['high'], BTCUSDT['low'], BTCUSDT['close'], 10, 3)

#print(sti['SUPERTd_10_3.0'][-1:])

if __name__ == "__main__":
    #first data fetch
    re_info()
    print_my_info()

    BTCUSDT_1h = OHLCV_Stream.get_historical_data(None)
    BTCUSDT_15m = OHLCV_Stream.get_historical_data(fetch_15m(date_limit))
    BTCUSDT_5m = OHLCV_Stream.get_historical_data(fetch_5m(date_limit))
    BTCUSDT_1m = OHLCV_Stream.get_historical_data(fetch_1m(date_limit))

    sti = ta.supertrend(BTCUSDT_1h['high'], BTCUSDT_1h['low'], BTCUSDT_1h['close'], 10, 3)
    sti_15m = ta.supertrend(BTCUSDT_15m['high'], BTCUSDT_15m['low'], BTCUSDT_15m['close'], 10, 3)
    sti_5m = ta.supertrend(BTCUSDT_5m['high'], BTCUSDT_5m['low'], BTCUSDT_5m['close'], 10, 3)
    sti_1m = ta.supertrend(BTCUSDT_1m['high'], BTCUSDT_1m['low'], BTCUSDT_1m['close'], 10, 3)
    #print(sti.iloc[-1]['SUPERTd_10_3.0'])
    print("sti_1h",sti['SUPERTd_10_3.0'][-1])
    print("sti_15m", sti_15m['SUPERTd_10_3.0'][-1])
    print("sti_5m", sti_5m['SUPERTd_10_3.0'][-1])
    print("sti_1m", sti_1m['SUPERTd_10_3.0'][-1])
    if(sti['SUPERTd_10_3.0'][-1] == 1):
        ST = 'long'
    elif (sti['SUPERTd_10_3.0'][-1] == -1):
        ST = 'short'


    while(1):
        date = datetime.datetime.now()
        time = date.strftime('%H:%M:%S')
        sys.stdout.write("\r{0}".format(time))
        sys.stdout.flush()
        sec = (str(time).split(':'))[2]
        min = (str(time).split(':'))[1]
        n = int(min) % 10

        BTC_1h = fetch_1h()
        BTC_15m = fetch_15m(1)
        BTC_5m = fetch_5m(1)
        BTC_1m = fetch_1m(1)
        if (min == '00' and sec == '00'):
            print("\radd")
            BTCUSDT_1h = OHLCV_Stream.add_data(BTCUSDT_1h,BTC_1h)
            sti = ta.supertrend(BTCUSDT_1h['high'], BTCUSDT_1h['low'], BTCUSDT_1h['close'], 10, 3)
            print_my_info()
            #print(sti['SUPERTd_10_3.0'][-1])

        elif(sec == '00'):
            BTCUSDT_1h = OHLCV_Stream.replace_data(BTCUSDT_1h,BTC_1h)
            #print("",BTCUSDT['close'][-1])
            sti = ta.supertrend(BTCUSDT_1h['high'], BTCUSDT_1h['low'], BTCUSDT_1h['close'], 10, 3)
            #print(sti['SUPERTd_10_3.0'][-1])


        if(sec == '00'): #1분마다 갱신
            re_info() # 정보 갱신
            if(n == 0):
                #print_my_info()
                telegram_bot.send_info()

            MA_25_1h = talib.MA(BTCUSDT_1h['close'], timeperiod=25)
            #print("", BTCUSDT['close'][-1])
            #print("",MA_25_1h[-1],sti['SUPERTd_10_3.0'][-1])
            if (sti['SUPERTd_10_3.0'][-1] == 1):
                ST = 'long'
            elif (sti['SUPERTd_10_3.0'][-1] == -1):
                ST = 'short'

            #####################################################
            print("",ST,BTCUSDT_1h['close'][-1]- MA_25_1h[-1])
            if (my_position != 'n/a' and ROE > take_profit):
                # close_my_position()
                pass

            if(my_position == 'n/a'): # 포지션이 없을때
                if (ST == 'long'):
                    if (BTCUSDT_1h['close'][-1] < MA_25_1h[-1]):
                        open_long_position()
                        #telegram_bot.send_message("long open")
                    else:
                        pass
                elif (ST == 'short'):
                    if (BTCUSDT_1h['close'][-1] > MA_25_1h[-1]):
                        open_short_position()
                        #telegram_bot.send_message("short open")
                    else:
                        pass
            elif(my_position == 'long'):
                if (ST == 'long'):
                    pass
                elif (ST == 'short'):
                    if (BTCUSDT_1h['close'][-1] > MA_25_1h[-1]):
                        close_short_position()
                        open_short_position()
                        #telegram_bot.send_message("long close short open")
                    else:
                        pass
            elif (my_position == 'short'):
                if (ST == 'long'):
                    if (BTCUSDT_1h['close'][-1] < MA_25_1h[-1]):
                        close_short_position()
                        open_long_position()
                        #telegram_bot.send_message("long close short open")
                    else:
                        pass
                elif (ST == 'short'):
                    pass

            #######################################################
            #if (my_position == 'n/a'):  # 포지션이 없을때
            #    my_position = ST
                # telegram_bot.send_message(ST+" open")
            #else:  # 포지션이 있을때
            #    if (my_position == ST):  # 내 포지션과 ST가 같으면 가만히 있음
            #        pass
            #    else:  # 다르면 포지션 변경
            #        my_position = ST
                    # telegram_bot.send_message(my_position+" close "+ST+" open")


        TIME.sleep(1)