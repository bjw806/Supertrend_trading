import Option
import telegram_bot


def ccxt_graph():
    ohlcv_15m = binance.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=12)
    ohlcv_15m_for_ma = binance.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=112)
    ohlcv_1h = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=6)
    ohlcv_1h_for_ma = binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=106)

    open_1h, high_1h, low_1h, close_1h, volume_1h, date_1h, close_1h_pd = [], [], [], [], [], [], []
    open_15m, high_15m, low_15m, close_15m, volume_15m, date_15m, close_15m_pd = [], [], [], [], [], [], []

    for x in range(6):
        open_1h.append(float(ohlcv_1h[x][1]))
        high_1h.append(float(ohlcv_1h[x][2]))
        low_1h.append(float(ohlcv_1h[x][3]))
        close_1h.append(float(ohlcv_1h[x][4]))
        volume_1h.append(float(ohlcv_1h[x][5]))
        date_1h.append(ohlcv_1h[x][0])
    for x in range(106):
        close_1h_pd.append(float(ohlcv_1h_for_ma[x][4]))
    for x in range(12):
        open_15m.append(float(ohlcv_15m[x][1]))
        high_15m.append(float(ohlcv_15m[x][2]))
        low_15m.append(float(ohlcv_15m[x][3]))
        close_15m.append(float(ohlcv_15m[x][4]))
        volume_15m.append(float(ohlcv_15m[x][5]))
        date_15m.append(ohlcv_15m[x][0])
    for x in range(112):
        close_15m_pd.append(float(ohlcv_15m_for_ma[x][4]))

    MA_7_1h = talib.MA(numpy.array(close_1h_pd), timeperiod=7)
    MA_25_1h = talib.MA(numpy.array(close_1h_pd), timeperiod=25)
    MA_99_1h = talib.MA(numpy.array(close_1h_pd), timeperiod=99)
    MA_7_15m = talib.MA(numpy.array(close_15m_pd), timeperiod=7)
    MA_25_15m = talib.MA(numpy.array(close_15m_pd), timeperiod=25)
    MA_99_15m = talib.MA(numpy.array(close_15m_pd), timeperiod=99)

    fig = plt.figure(num=1, figsize=(7.5, 7.55), dpi=50, facecolor='w', edgecolor='k') # figsize: ppi dpi: 해상도
    gs = GridSpec(nrows=10, ncols=1)######비율
    cx_1h = fig.add_subplot(gs[0:4, 0]) #111은 subplot 그리드 인자를 정수 하나에 다 모아서 표현한 것.(1x1그리드에 첫 번째 subplot)
    vx_1h = fig.add_subplot(gs[4, 0]) #볼륨차트 추가
    cx_15m = fig.add_subplot(gs[5:9, 0])
    vx_15m = fig.add_subplot(gs[9, 0])
    mpl_finance.volume_overlay(vx_1h, open_1h, close_1h, volume_1h, width=0.4, colorup='r', colordown='b', alpha=1)
    mpl_finance.candlestick2_ochl(cx_1h, open_1h,close_1h,high_1h,low_1h, width=0.965, colorup='r', colordown='b', alpha=1)
    mpl_finance.volume_overlay(vx_15m, open_15m, close_15m, volume_15m, width=0.4, colorup='r', colordown='b', alpha=1)
    mpl_finance.candlestick2_ochl(cx_15m, open_15m, close_15m, high_15m, low_15m, width=0.965, colorup='r', colordown='b', alpha=1)
    plt.autoscale()  # 자동 스케일링

    line_width = 4
    cx_1h.plot(MA_7_1h[99:], color='gold', linewidth=line_width, alpha=1)#99+~이니까 99부터 시작
    cx_1h.plot(MA_25_1h[99:], color='violet', linewidth=line_width, alpha=1)
    cx_1h.plot(MA_99_1h[99:], color='green', linewidth=line_width, alpha=1)
    cx_15m.plot(MA_7_15m[99:], color='gold', linewidth=line_width, alpha=1)
    cx_15m.plot(MA_25_15m[99:], color='violet', linewidth=line_width, alpha=1)
    cx_15m.plot(MA_99_15m[99:], color='green', linewidth=line_width, alpha=1)
    plt.axis('off')  # 상하좌우 축과 라벨 모두 제거
    vx_1h.axis('off')
    cx_1h.axis('off')
    cx_15m.axis('off')
    vx_15m.axis('off')

    plt.savefig('../test_data/ccxt_binance_test_2g_1h_15m.jpg', bbox_inches='tight')  # uuid.uuid4()
    # plt.show()
    plt.cla()  # 좌표축을 지운다.
    plt.clf()  # 현재 Figure를 지운다.

def predict(file):
    x = load_img(file, target_size=(img_width,img_height))
    x = img_to_array(x)
    x = numpy.expand_dims(x, axis=0)
    array = model.predict(x)
    result = array[0]
    precision = 0
    if result[0] > result[1]:
        if result[0] > 0.55:
            print("Predicted: Long")
            answer = 'long'
            precision = result[0]
        else:
            print("Predicted: Not confident long")
            answer = 'n/a long'
            precision = result[0]
            print(result)
    else:
        if result[1] > 0.55:
            print("Predicted: Short")
            answer = 'short'
            precision = result[1]
        else:
            print("Predicted: Not confident short")
            answer = 'n/a short'
            precision = result[1]
            print(result)
    prec = f'{precision:0.4f}'
    return answer, prec

def trade(input_pos, precision):
    if (input_pos == 'long'):  # and PNL >= 0
        if (my_position == 'short'):
            print("[Long Position]")
            close_short_position()
            open_long_position()
        elif (my_position == 'n/a'):
            print("[Long Position]")
            open_long_position()
        else:
            print("Already have same position")
        return
    elif (input_pos == 'short'):  # and PNL >= 0
        if (my_position == 'long'):
            print("[Short Position]")
            close_long_position()
            open_short_position()
        elif (my_position == 'n/a'):
            print("[Short Position]")
            open_short_position()
        else:
            print("Already have same position")
        return
    else:
        print("N/A")

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

def Take_Profit():
    if (ROE > take_profit):
        print("[Take Profit]")
        if (my_position == 'long'):
            close_long_position()
        elif (my_position == 'short'):
            close_short_position()


if __name__ == "__main__":
    re_info()
    print(assets)
    print_my_info()
    close_in_min = 5
    open_time_min = 0
    ccxt_graph()
    answer, precision = predict(predict_file)
    print("          Precision:", precision)
    predicted_temp = answer
    while(1):
        date = datetime.datetime.now()
        time = date.strftime('%H:%M:%S')
        sys.stdout.write("\r{0}".format(time))
        sys.stdout.flush()
        sec = (str(time).split(':'))[2]
        min = (str(time).split(':'))[1]
        m = int(min) % 59
        n = int(min) % 5
        if((min != '59' and min != '04') and sec == '55'):
            re_info()
            Take_Profit()
        if((min == '59' or min == '04') and sec == '57'):
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            t = "\r\n==========|" + date + "|=========="
            print(t)
            ccxt_graph()
            answer, precision = predict(predict_file)
            if(min == '59'):
                predicted_temp = answer
                close_my_position()
            re_info()
            prec = " " + str(float(precision) * 100) + " %"
            print("          Precision:", prec)
            # print(date, precision)
            if(min == '04' and predicted_temp == answer):
                trade(answer, float(precision))
                predicted_temp = 'n/a'
            # open_time_min = int(min)
            print("My Position:", my_position)
            print("unrealizedProfit:", PNL)
            print("ROE:", ROE)
            print("\r\n")

        if (n == 4 and sec == '57'):
            if(min != '00'):
                re_info()
                print_my_info()
                ccxt_graph()
                answer, precision = predict(predict_file)
            prec = " " + str(float(precision) * 100) + " %"
            print("          Precision:", prec)
            telegram_bot.send_prediction(answer, precision)
            TIME.sleep(1)
        else:
            TIME.sleep(1)

