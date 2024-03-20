import pyupbit
import time
from datetime import datetime
import pymysql
import random

db = pymysql.connect(host='swc9004.iptime.org', user='swc', password='core2020', db='anteUpbit', charset='utf8')
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
    cur = db.cursor()
    row = None
    setkey = None
    try:
        sql = '''SELECT userNo, userName FROM pondUser WHERE userId=%s AND userPasswd=password(%s) AND attrib NOT LIKE %s'''
        cur.execute(sql, (uid, upw, str("%XXX")))
        row = cur.fetchone()
        if row is not None:
            setkey = random.randint(100000,999999)
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return row, setkey

def setKeys(uno, setkey):
    cur = db.cursor()
    try:
        sql = "UPDATE pondUser SET setupKey = %s, lastLogin = now() where userNo=%s"
        cur.execute(sql, (setkey, uno))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()

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

def checkwallet(uno, setkey):
    walletitems = []
    cur = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql,(setkey, uno, '%XXX'))
    keys = cur.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        walletitems = upbit.get_balances()
    return walletitems

def tradehistory(uno, setkey):
    tradelist = []
    cur = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql,(setkey, uno, '%XXX'))
    keys = cur.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        tradelist = upbit.get_order("KRW-ETH",state='done')
        print(tradelist)
    return tradelist

def checkkey(uno, setkey):
    cur = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql,(setkey, uno, '%XXX'))
    result = cur.fetchall()
    if len(result) == 0:
        print("No match Keys !!")
        return False
    else:
        return True

def erasebid(uno, setkey):
    cur = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql,(setkey, uno, '%XXX'))
    result = cur.fetchall()
    if len(result) == 0:
        print("No match Keys !!")
        return False
    else:
        sql2 = "update tradingSetup set attrib=%s where userNo=%s"
        cur.execute(sql2,("XXXUPXXXUPXXXUP", uno))
        db.commit()
        return True

def setupbid(uno, setkey, initbid, bidstep, bidrate, askrate, coinn):
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        try:
            erasebid(uno, setkey)
            cur = db.cursor()
            sql = "insert into tradingSetup (userNo, initAsset, bidInterval, bidRate, askrate, bidCoin) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (uno, initbid, bidstep, bidrate, askrate, coinn))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur.close()
            return True
    else:
        return False
