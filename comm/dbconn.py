import pyupbit
import time
from datetime import datetime
import pymysql
import random

db = pymysql.connect(host='swc9004.iptime.org', user='swcdjk', password='core2020', db='anteUpbit', charset='utf8')
cur = db.cursor()
serverNo = 2

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


def selectUsers(uid, upw):
    cur = db.cursor()
    row = None
    setkey = None
    try:
        sql = "SELECT userNo, userName, serverNo, userRole FROM pondUser WHERE userPasswd=password(%s) AND userId=%s AND attrib NOT LIKE %s"
        cur.execute(sql, (upw, uid, str("%XXX")))
        row = cur.fetchone()
        print(row)
        if row is not None:
            setkey = random.randint(100000,999999)
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return row, setkey


def listUsers():
    global rows
    cur = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE attrib NOT LIKE %s"
        cur.execute(sql, str("%XXX"))
        rows = cur.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return rows

def detailuser(uno):
    global rows
    cur = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE userNo = %s and attrib NOT LIKE %s"
        cur.execute(sql, (uno,str("%XXX")))
        rows = cur.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return rows


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
    global key1, key2, walletitems
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
        print(walletitems)
    cur.close()
    return walletitems


def checkwalletwon(uno, setkey):
    global key1, key2, walletwon
    walletwon = []
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
        walletwon = round(upbit.get_balance("KRW"))
    cur.close()
    return walletwon


def tradehistory(uno, setkey):
    tradelist = []
    cur = db.cursor()
    sql = "SELECT bidCoin from tradingSetup where userNo = %s and attrib not like %s "
    cur.execute(sql,(uno, '%XXXUP'))
    data = cur.fetchone()
    coinn = data[0]
    sql2 = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql2,(setkey, uno, '%XXX'))
    keys = cur.fetchone()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0]
        key2 = keys[1]
        upbit = pyupbit.Upbit(key1,key2)
        tradelist = upbit.get_order(coinn,state='done')
    cur.close()
    return tradelist


def checkkey(uno, setkey):
    cur = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur.execute(sql,(setkey, uno, '%XXX'))
    result = cur.fetchall()
    cur.close()
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
    cur.close()
    if len(result) == 0:
        print("No match Keys !!")
        return False
    else:
        sql2 = "update tradingSetup set attrib=%s where userNo=%s"
        cur.execute(sql2,("XXXUPXXXUPXXXUP", uno))
        db.commit()
        return True


def setupbid(uno, setkey, initbid, bidstep, bidrate, askrate, coinn, svrno):
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        try:
            erasebid(uno, setkey)
            cur = db.cursor()
            sql = "insert into tradingSetup (userNo, initAsset, bidInterval, bidRate, askrate, bidCoin, serverNo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (uno, initbid, bidstep, bidrate, askrate, coinn, svrno))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur.close()
            return True
    else:
        return False


def setupbidadmin(uno, setkey, settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9):
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        try:
            cur = db.cursor()
            sql = ("insert into tradingSets (setTitle, setInterval, step0, step1, step2, step3, step4, step5, step6, step7, step8, step9, inter0, inter1, inter2, inter3, inter4, inter5, inter6, inter7, inter8, inter9, regdate) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())")
            cur.execute(sql, (settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8,int9, ))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur.close()
            return True
    else:
        return False


def getsetup(uno):
    try:
        cur = db.cursor()
        sql = "SELECT bidCoin, initAsset, bidInterval, bidRate, askRate, activeYN from tradingSetup where userNo=%s and attrib not like %s"
        cur.execute(sql, (uno, '%XXXUP'))
        data = list(cur.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()


def getsetups(uno):
    try:
        cur = db.cursor()
        sql = "select * from tradingSetup where userNo=%s and attrib not like %s"
        cur.execute(sql, (uno, '%XXXUP'))
        data = list(cur.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()


def setonoff(uno,yesno):
    cur = db.cursor()
    try:
        sql = "UPDATE tradingSetup SET activeYN = %s where userNo=%s AND attrib not like %s"
        cur.execute(sql, (yesno, uno,'%XXXUP'))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()


def getseton():
    cur = db.cursor()
    data = []
    print("GetKey !!")
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s"
        cur.execute(sql,'%XXXUP')
        data = cur.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur.close()

def getsetonsvr(svrNo):
    cur = db.cursor()
    data = []
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s and serverNo=%s"
        cur.execute(sql,('%XXXUP', svrNo))
        data = cur.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur.close()


def getupbitkey(uno):
    cur = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE userNo=%s and attrib not like %s"
        cur.execute(sql, (uno,'%XXXUP'))
        data = cur.fetchone()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur.close()


def clearcache():
    cur = db.cursor()
    sql = "RESET QUERY CACHE"
    cur.execute(sql)
    cur.close()


def getorderlist(uno):
    keys = getupbitkey(uno)
    setups = getsetup(uno)
    coinn = setups[0]
    upbit = pyupbit.Upbit(keys[0],keys[1])
    orders = upbit.get_order(coinn)
    return orders


def sellmycoin(uno,coinn):
    keys = getupbitkey(uno)
    upbit = pyupbit.Upbit(keys[0],keys[1])
    walt = upbit.get_balances()
    print(coinn)
    for coin in walt:
        if coin['currency'] == coinn:
            balance = float(coin['balance'])
            coinn = "KRW-"+ coinn
            result = upbit.sell_market_order(coinn,balance)
            try:
                if result["error"]["name"] == 'under_min_total_market_ask':
                    buy5000 = upbit.buy_market_order(coinn, 5000)
                    print(buy5000)
            except Exception as e:
                pass
        else:
            pass


def selectsets():
    global rows
    cur = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE attrib NOT LIKE %s"
        cur.execute(sql, str("%XXX"))
        rows = cur.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return rows


def setdetail(setno):
    global rows
    cur = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE setNo = %s"
        cur.execute(sql, setno)
        rows = cur.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur.close()
    return rows