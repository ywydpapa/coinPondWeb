import pyupbit
import pymysql


db=pymysql.connect(host='swc9004.iptime.org', user='swc',
                     password='core2020', db='anteUpbit',
                     charset='utf8')
cur=db.cursor()


def check_srv(coinn, perc):
    values = pyupbit.get_ohlcv(coinn, interval="hour", count=48)
    volumes = values['volume']
    if len(volumes) < 21:
        return False
    sum_vol20 = 0
    today_vol = 0
    for i, vol in enumerate(volumes):
        if i == 0:
            today_vol = vol
        elif 1 <= i <= 20:
            sum_vol20 += vol
        else:
            break
    avg_vol20 = sum_vol20 / 20
    if today_vol > avg_vol20 * perc:
        return True


def get_candle(coinn):
    candles = pyupbit.get_ohlcv(coinn, interval="minutes60", count=72)
    volumes = candles['volume']
    values = candles['value']
    prices = candles['close']
    print(prices)


get_candle("KRW-ETH")