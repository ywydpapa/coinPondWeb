from flask import jsonify
import requests
import pyupbit
import json
import time

from pandas import DataFrame


def dashcandle548(coinn):
    candles: DataFrame | None = pyupbit.get_ohlcv(coinn, interval="minute5", count=48)
    return candles


def dashcandle160(coinn):
    candles: DataFrame | None = pyupbit.get_ohlcv(coinn, interval="minute1", count=60)
    return candles


def get_ticker_tradevalue():
    tickers = pyupbit.get_tickers("KRW")
    dic_ticker = {}
    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, 'day', count=1)
        volume_money = 0.0
        volume_money += df['close'][0] * df['volume'][0]
        dic_ticker[ticker] = volume_money
        time.sleep(0.1)
    sorted_ticker = sorted(dic_ticker.items(), key=lambda x: x[1], reverse=True)
    return sorted_ticker
