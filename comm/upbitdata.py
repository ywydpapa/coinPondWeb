from flask import jsonify
import requests
import json

def dashcandle548(coinn):
    url = "https://api.upbit.com/v1/candles/minutes/5?count=48&market="+coinn
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return jsonify(response.text)