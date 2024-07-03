from flask import jsonify
import requests
import pyupbit
import json

from pandas import DataFrame


def dashcandle548(coinn):
    candles: DataFrame | None = pyupbit.get_ohlcv(coinn, interval="minute5", count=48)
    return candles