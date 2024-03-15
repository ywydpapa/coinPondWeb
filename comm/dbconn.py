import pyupbit
import time
from datetime import datetime
import pymysql


db = pymysql.connect(host='192.168.108.198', user='swc', password='core2020', db='anteUpbit', charset='utf8')
cur = db.cursor()

def check_srv(coinn, perc):
    values = pyupbit.get_ohlcv(coinn, interval="day", count=30)
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

def selectUsers(uid, upw):
    row = None
    connection = None
    try:
        sql = '''SELECT userNo, userName, setupKey FROM pondUser WHERE userId=%s AND userPasswd=password(%s) AND attrib NOT LIKE %s'''
        cur.execute(sql, (uid, upw, str("%XXX")))
        row = cur.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        if connection:
            connection.close()
    return row

def check_srv(coinn,perc):
    values = pyupbit.get_ohlcv(coinn, interval="day", count=30)
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