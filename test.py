import time
import pyupbit

tickers = pyupbit.get_tickers("KRW")
dic_ticker = {}

for ticker in tickers:
    df = pyupbit.get_ohlcv(ticker, 'day', count=3)
    print(df)
    volume_money = 0.0
    for i in range(1, 3):
        volume_money += df['close'][-i] * df['volume'][-i]
    dic_ticker[ticker] = volume_money
    time.sleep(0.1)

sorted_ticker = sorted(dic_ticker.items(), key= lambda x : x[1], reverse= True)

coin_list = []
count = 0

for coin in sorted_ticker:
    count += 1

    if count <= 10:
        coin_list.append(coin[0])
    else:
        break

print(coin_list)

