# 거래 함수

import Calculate_ST
import OHLCV_Stream
import time as TIME
import datetime
import sys
import pandas as pd
import Option
import telegram_bot
import Plot

binance_futures = Option.binance_futures
trade_amount = Option.trade_amount

def open_long_position():
    global my_position
    my_position = 'long'
    print('[Long Open]')
    order = binance_futures.create_market_buy_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Long", "Open", trade_amount, 0, total_profit)
    #pprint.pprint(order)

def open_short_position():
    global my_position
    my_position = 'short'
    print('[Short Open]')
    order = binance_futures.create_market_sell_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Short", "Open", trade_amount, 0, total_profit)
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
    order = binance_futures.create_market_sell_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Long", "Close", trade_amount, PNL, total_profit)
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
    order = binance_futures.create_market_buy_order(symbol="BTC/USDT", amount=trade_amount)
    price = order["price"]
    cost = order["cost"]
    telegram_bot.send_trading_message(price, cost, "Short", "Close", trade_amount, PNL, total_profit)
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



if __name__ == "__main__":
    #first data fetch
    BTCUSDT = OHLCV_Stream.get_historical_data()
    print(BTCUSDT)
    while(1):
        date = datetime.datetime.now()
        time = date.strftime('%H:%M:%S')
        sys.stdout.write("\r{0}".format(time))
        sys.stdout.flush()
        sec = (str(time).split(':'))[2]
        min = (str(time).split(':'))[1]

        if(sec == '57'):
            if ((min == '59') and sec == '57'):
                print("\radd")
                BTCUSDT = OHLCV_Stream.add_data(BTCUSDT)

                print(Option.my_position)

            if (min != '59' and sec == '57'):
                print("\rreplace")
                BTCUSDT = OHLCV_Stream.replace_data(BTCUSDT)

            ST_BTCUSDT, st_signal, st_position,buy_price,sell_price = Calculate_ST.ST_stream(BTCUSDT)
            Plot.ploting(ST_BTCUSDT,buy_price,sell_price)

            #print(Calculate_ST.ST_stream()[40:70])
            if (st_signal.iloc[-1]['st_signal'] == 1 and st_position.iloc[-1]['st_position'] == 1):
                print("switch to long")
                Option.my_position = 'long'
                telegram_bot.send_message("long")
            elif (st_signal.iloc[-1]['st_signal'] == -1 and st_position.iloc[-1]['st_position'] == 0):
                print("switch to short")
                Option.my_position = 'short'
                telegram_bot.send_message("short")
            elif (st_signal.iloc[-1]['st_signal'] == 0) :
                print(st_signal.iloc[-1]['st_signal'],st_position.iloc[-1]['st_position'])
                print("Nothing")

        TIME.sleep(1)
        # position -> 1=buy  2=sell