from flask import jsonify
import requests
import pyupbit
import json
import time, datetime
import pymysql
import dotenv
from pandas import DataFrame
import os


dotenv.load_dotenv()
hostenv = os.getenv("host")
userenv = os.getenv("user")
passwordenv = os.getenv("password")
dbenv = os.getenv("db")
charsetenv = os.getenv("charset")


def get_ticker_tradevalueDaemon():  # 핫코인 추가
    tickers = pyupbit.get_tickers("KRW")
    dic_ticker = {}
    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, 'day', count=1)
        volume_money = 0.0
        volume_money += df['close'][0] * df['volume'][0]
        dic_ticker[ticker] = volume_money
        time.sleep(0.1)
    sorted_ticker = sorted(dic_ticker.items(), key=lambda x: x[1], reverse=True)
    coin_list = []
    count = 0
    tstamp = datetime.datetime.now()
    tstamp = tstamp.strftime("%Y-%m-%d %H:%M")
    db31 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur31 = db31.cursor()
    sql = "update coinTradeAmt set attrib = %s"
    cur31.execute(sql, ("XXXUPXXXUPXXXUP"))
    db31.commit()
    for coin in sorted_ticker:
        try:
            sql = "INSERT into coinTradeAmt (coinName, tradeAmt, getDate) values (%s,%s,%s)"
            cur31.execute(sql, (coin[0], coin[1], tstamp))
            db31.commit()
        except Exception as e:
            print('코인 거래량 업로드 오류', e)
        finally:
            pass
    cur31.close()
    db31.close()
