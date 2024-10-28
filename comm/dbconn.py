import os
import random
from datetime import datetime, timedelta
from typing import List, Any

import dotenv
import pymysql
import pyupbit
import jwt
import hashlib
import requests
import uuid
from urllib.parse import urlencode, unquote
import json

from dotenv import get_key

dotenv.load_dotenv()
hostenv = os.getenv("host")
userenv = os.getenv("user")
passwordenv = os.getenv("password")
dbenv = os.getenv("db")
charsetenv = os.getenv("charset")


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
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur1 = db.cursor()
    row = None
    setkey = None
    try:
        sql = "SELECT userNo, userName, serverNo, userRole FROM pondUser WHERE userPasswd=password(%s) AND userId=%s AND attrib NOT LIKE %s"
        cur1.execute(sql, (upw, uid, str("%XXX")))
        row = cur1.fetchone()
        print(row)
        if row is not None:
            setkey = random.randint(100000,999999)
    except Exception as e:
        print('접속오류', e)
    finally:
        cur1.close()
        db.close()
    return row, setkey


def listUsers():
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur2 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE attrib NOT LIKE %s"
        cur2.execute(sql, str("%XXX"))
        rows = cur2.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur2.close()
        db.close()
    return rows


def detailuser(uno):
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur3 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM pondUser WHERE userNo = %s and attrib NOT LIKE %s"
        cur3.execute(sql, (uno,str("%XXX")))
        rows = cur3.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur3.close()
        db.close()
    return rows


def setKeys(uno, setkey):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur4 = db.cursor()
    try:
        sql = "UPDATE pondUser SET setupKey = %s, lastLogin = now() where userNo=%s"
        cur4.execute(sql, (setkey, uno))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur4.close()
        db.close()


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
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur5 = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur5.execute(sql,(setkey, uno, '%XXX'))
    keys = cur5.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        walletitems = upbit.get_balances()
    cur5.close()
    db.close()
    return walletitems


def checkwalletwon(uno, setkey):
    global key1, key2, walletwon
    walletwon = []
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur6 = db.cursor()
    sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur6.execute(sql,(setkey, uno, '%XXX'))
    keys = cur6.fetchall()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0][0]
        key2 = keys[0][1]
        upbit = pyupbit.Upbit(key1,key2)
        walletwon = round(upbit.get_balance("KRW"))
    cur6.close()
    db.close()
    return walletwon


def tradehistory(uno, setkey):
    tradelist = []
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur7 = db.cursor()
    sql = "SELECT bidCoin from tradingSetup where userNo = %s and attrib not like %s "
    cur7.execute(sql,(uno, '%XXXUP'))
    data = cur7.fetchone()
    coinn = data[0]
    sql2 = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur7.execute(sql2,(setkey, uno, '%XXX'))
    keys = cur7.fetchone()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0]
        key2 = keys[1]
        upbit = pyupbit.Upbit(key1,key2)
        tradelist = upbit.get_order(coinn,state='done')
    cur7.close()
    db.close()
    return tradelist


def tradehistorys(uno, setkey, coinn):
    tradelist2 = []
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur7 = db.cursor()
    sql2 = "SELECT apiKey1, apiKey2 FROM pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur7.execute(sql2,(setkey, uno, '%XXX'))
    keys = cur7.fetchone()
    if len(keys) == 0:
        print("No available Keys !!")
    else:
        key1 = keys[0]
        key2 = keys[1]
        upbit = pyupbit.Upbit(key1,key2)
        tradelist2 = upbit.get_order(coinn,state='done')
    cur7.close()
    db.close()
    return tradelist2


def checkkey(uno, setkey):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur8 = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur8.execute(sql,(setkey, uno, '%XXX'))
    result = cur8.fetchall()
    cur8.close()
    db.close()
    if len(result) == 0:
        print("No match Keys !!")
        return False
    else:
        return True


def erasebid(uno, setkey):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur9 = db.cursor()
    sql = "SELECT * from pondUser WHERE setupKey=%s AND userNo=%s and attrib not like %s"
    cur9.execute(sql,(setkey, uno, '%XXX'))
    result = cur9.fetchall()
    if len(result) == 0:
        print("No match Keys !!")
        cur9.close()
        db.close()
        return False
    else:
        sql2 = "update tradingSetup set attrib=%s where userNo=%s"
        cur9.execute(sql2,("XXXUPXXXUPXXXUP", uno))
        db.commit()
        cur9.close()
        db.close()
        return True



def setupbid(uno, setkey, initbid, bidstep, bidrate, askrate, coinn, svrno, tradeset, holdNo, doubleYN):
    global cur0, db
    chkkey = checkkey(uno, setkey)
    nowt = datetime.now()+ timedelta(minutes=15)
    if chkkey == True:
        try:
            db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
            cur0 = db.cursor()
            sql = "insert into tradingSetup (userNo, initAsset, bidInterval, bidRate, askrate, bidCoin, custKey ,serverNo, holdNo, doubleYN, regDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())"
            cur0.execute(sql, (uno, initbid, bidstep, bidrate, askrate, coinn, tradeset, svrno, holdNo, doubleYN))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur0.close()
            db.close()
            tradelog(uno,'HOLD',coinn,nowt)
            tradelog(uno, 'BID', coinn, nowt)
            return True
    else:
        return False


def editbidsetup(sno, uno, setkey, initbid, bidstep, bidrate, askrate, coinn, svrno, tradeset, holdNo, doubleYN):
    global cur0, db
    chkkey = checkkey(uno, setkey)
    nowt = datetime.now()+ timedelta(minutes=15)
    if chkkey == True:
        try:
            db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
            cur0 = db.cursor()
            sqlp = "update tradingSetup set attrib=%s where setupNo=%s"
            cur0.execute(sqlp,("XXXUPXXXUPXXXUP", sno))
            db.commit()
            sql = "insert into tradingSetup (userNo, initAsset, bidInterval, bidRate, askrate, bidCoin, custKey ,serverNo, holdNo, doubleYN, regDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())"
            cur0.execute(sql, (uno, initbid, bidstep, bidrate, askrate, coinn, tradeset, svrno, holdNo, doubleYN))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur0.close()
            db.close()
            tradelog(uno,'HOLD',coinn,nowt)
            tradelog(uno, 'BID', coinn, nowt)
            return True
    else:
        return True


def setupbidadmin(uno, setkey, settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9, hno, dyn):
    global cur11, db
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        try:
            db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
            cur11 = db.cursor()
            sql = ("insert into tradingSets (setTitle, setInterval, step0, step1, step2, step3, step4, step5, step6, step7, step8, step9, inter0, inter1, inter2, inter3, inter4, inter5, inter6, inter7, inter8, inter9, holdNo, doubleYN, regdate) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())")
            cur11.execute(sql, (settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8,int9,hno,dyn ))
            db.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur11.close()
            db.close()
            return True
    else:
        return False


def getsetup(uno):
    global cur12, db
    try:
        db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
        cur12 = db.cursor()
        sql = "SELECT bidCoin, initAsset, bidInterval, bidRate, askRate, activeYN, custKey, holdYN, holdNo, doubleYN  from tradingSetup where userNo=%s and attrib not like %s"
        cur12.execute(sql, (uno, '%XXXUP'))
        data = list(cur12.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur12.close()
        db.close()


def getsetupmax(uno,sdate):
    global cur12, db
    try:
        db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
        cur12 = db.cursor()
        sql = "SELECT bidCoin, initAsset, bidInterval, bidRate, askRate, activeYN, custKey, holdYN, holdNo, doubleYN  from tradingSetup where userNo=%s and regDate <= %s order by regDate desc"
        cur12.execute(sql, (uno, sdate))
        data = list(cur12.fetchone())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur12.close()
        db.close()


def getsetups(uno):
    try:
        db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
        cur13 = db.cursor()
        sql = "select * from tradingSetup where userNo=%s and attrib not like %s"
        cur13.execute(sql, (uno, '%XXXUP'))
        data = list(cur13.fetchall())
        return data
    except Exception as e:
        print('접속오류', e)
    finally:
        cur13.close()
        db.close()


def setonoff(uno,yesno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur14 = db.cursor()
    try:
        sql = "UPDATE tradingSetup SET activeYN = %s where userNo=%s AND attrib not like %s"
        cur14.execute(sql, (yesno, uno,'%XXXUP'))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur14.close()
        db.close()


def setonoffs(setno,yesno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur14 = db.cursor()
    try:
        sql = "UPDATE tradingSetup SET activeYN = %s where setupNo=%s AND attrib not like %s"
        cur14.execute(sql, (yesno, setno,'%XXXUP'))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur14.close()
        db.close()


def setholdreset(uno,hr):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur14_1 = db.cursor()
    try:
        sql = "UPDATE tradingSetup SET holdYN = %s where userNo=%s AND attrib not like %s"
        cur14_1.execute(sql, (hr, uno,'%XXXUP'))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur14_1.close()
        db.close()


def getseton():
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur15 = db.cursor()
    data = []
    print("GetKey !!")
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s"
        cur15.execute(sql,'%XXXUP')
        data = cur15.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur15.close()
        db.close()


def getsetonsvr(svrNo):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur16 = db.cursor()
    data = []
    try:
        sql = "SELECT userNo from tradingSetup where attrib not like %s and serverNo=%s"
        cur16.execute(sql,('%XXXUP', svrNo))
        data = cur16.fetchall()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur16.close()
        db.close()


def getupbitkey(uno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur17 = db.cursor()
    try:
        sql = "SELECT apiKey1, apiKey2 FROM pondUser WHERE userNo=%s and attrib not like %s"
        cur17.execute(sql, (uno,'%XXXUP'))
        data = cur17.fetchone()
        return data
    except Exception as e:
        print('접속오류',e)
    finally:
        cur17.close()
        db.close()


def clearcache():
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur18 = db.cursor()
    sql = "RESET QUERY CACHE"
    cur18.execute(sql)
    cur18.close()
    db.close()


def getorderlist(uno):
    keys = getupbitkey(uno)
    upbit = pyupbit.Upbit(keys[0], keys[1])
    setups = getsetups(uno)
    orders = []
    for setup in setups:
        coinn = setup[6]
        order = upbit.get_order(coinn)
        orders.extend(order)
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
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur19 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE attrib NOT LIKE %s"
        cur19.execute(sql, str("%XXX"))
        rows = cur19.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur19.close()
        db.close()
    return rows


def setdetail(setno):
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur20 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE setNo = %s"
        cur20.execute(sql, setno)
        rows = cur20.fetchone()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur20.close()
        db.close()
    return rows


def selectsetlist(sint):
    global rows
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur21 = db.cursor()
    row = None
    try:
        sql = "SELECT * FROM tradingSets WHERE useYN = %s and attrib NOT LIKE %s"
        if sint > 0:
            useyn = 'Y'
        cur21.execute(sql, (useyn, "XXX%"))
        rows = cur21.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur21.close()
        db.close()
    return rows


def setmypasswd(uno, passwd):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur22 = db.cursor()
    try:
        sql = "UPDATE pondUser SET userPasswd = password(%s) where userNo=%s"
        cur22.execute(sql, (passwd, uno))
        db.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur22.close()
        db.close()


def updateuserdetail(uno, key1, key2, svrno):
    db = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur23 = db.cursor()
    try:
        sql= "UPDATE pondUser SET apiKey1 = %s, apiKey2 = %s, serverNo = %s where userNo = %s"
        cur23.execute(sql, (key1, key2, svrno, uno))
        db.commit()
    except Exception as e:
        print('사용자 업데이트 오류', e)
    finally:
        cur23.close()
        db.close()


def updatebidadmin(uno, setkey, settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9, holdyn ,dblyn ,setsno):
    chkkey = checkkey(uno, setkey)
    if chkkey == True:
        db24 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
        cur24 = db24.cursor()
        try:
            sql = ("UPDATE tradingSets set setTitle = %s, setInterval = %s, step0 = %s, step1 = %s, step2 = %s, step3 = %s, step4 = %s, step5 = %s, step6 = %s, step7 = %s, step8 = %s, step9 = %s, "
                   "inter0 = %s, inter1 = %s, inter2 = %s, inter3 = %s, inter4 = %s, inter5 = %s, inter6 = %s, inter7 = %s, inter8 = %s, inter9 = %s, holdNo = %s, doubleYN = %s, modDate = now() where setNo = %s")
            cur24.execute(sql, (settitle, bidstep, stp0, stp1, stp2, stp3, stp4, stp5, stp6, stp7, stp8, stp9, int0, int1, int2, int3, int4, int5, int6, int7, int8, int9, holdyn, dblyn, setsno))
            db24.commit()
        except Exception as e:
            print('접속오류', e)
        finally:
            cur24.close()
            db24.close()
            return True
    else:
        return False


def settingonoff(sno, yesno):
    db25 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur25 = db25.cursor()
    try:
        sql = "UPDATE tradingSets SET useYN = %s where setNo=%s"
        cur25.execute(sql, (yesno, sno))
        db25.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur25.close()
        db25.close()


def hotcoinlist():
    global rows
    db26 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur26 = db26.cursor()
    row = None
    try:
        sql = "SELECT * from trendcoins where market in (SELECT coinName FROM hotCoins WHERE attrib NOT LIKE %s)"
        cur26.execute(sql, "XXX%")
        rows = cur26.fetchall()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur26.close()
        db26.close()
    return rows


def sethotcoin(coinn, yn):
    global rows
    db27 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur27 = db27.cursor()
    try:
        if yn == 'N':
            sql = "UPDATE hotCoins SET attrib = %s where coinName=%s"
            cur27.execute(sql, ("XXX00XXX00XXX00",coinn))
            db27.commit()
        else:
            sql = "UPDATE hotCoins SET attrib = %s where coinName=%s"
            cur27.execute(sql, ("XXX00XXX00XXX00", coinn))
            db27.commit()
            sql2 = "INSERT INTO hotCoins (coinName, regDate) VALUES (%s, now())"
            cur27.execute(sql2,coinn)
            db27.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur27.close()
        db27.close()


def selectboardlist(brdid):
    global rows
    db28 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur28 = db28.cursor()
    try:
        sql = "SELECT * FROM board WHERE boardId=%s and attrib NOT LIKE %s"
        cur28.execute(sql, (brdid,"XXX%"))
        rows = cur28.fetchall()
        return rows
    except Exception as e:
        print('게시판 조회 오류',e)
    finally:
        cur28.close()
        db28.close()


def boarddetail(brdno):
    global rows
    db29 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur29 = db29.cursor()
    try:
        sql = "SELECT * FROM board WHERE boardno=%s and attrib NOT LIKE %s"
        cur29.execute(sql, (brdno, "XXX%"))
        rows = cur29.fetchall()
        return rows
    except Exception as e:
        print('게시판 조회 오류', e)
    finally:
        cur29.close()
        db29.close()


def boardupdate(brdno, btitle, bcontents):
    global rows
    db30 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur30 = db30.cursor()
    try:
        sql = "UPDATE board SET title = %s, context = %s, modDate = now() where boardno=%s"
        cur30.execute(sql, (btitle, bcontents,brdno))
        db30.commit()
    except Exception as e:
        print('게시판 업데이트 오류',e)
    finally:
        cur30.close()
        db30.close()


def boardnewwrite(brdid, btitle, bcontents, userid):
    global rows
    db31 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur31 = db31.cursor()
    try:
        sql = "INSERT into board (boardId, title, context, userId, regDate, modDate) values (%s,%s,%s,%s,now(),now())"
        cur31.execute(sql, (brdid, btitle, bcontents, userid))
        db31.commit()
    except Exception as e:
        print('게시판 작성 오류',e)
    finally:
        cur31.close()
        db31.close()

def getmessage(uno):
    global rows
    db32 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur32 = db32.cursor()
    try:
        sql = "SELECT * FROM error_Log WHERE userNo=%s and attrib NOT LIKE %s"
        cur32.execute(sql, (uno, 'RRR%'))
        rows = cur32.fetchall()
        return rows
    except Exception as e:
        print('메세지 조회 오류', e)
    finally:
        cur32.close()
        db32.close()


def readmsg(errno):
    db33 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur33 = db33.cursor()
    try:
        sql = "UPDATE error_Log SET attrib = %s where errorNo=%s"
        cur33.execute(sql, ("RRR00RRR00RRR00", errno))
        db33.commit()
    except Exception as e:
        print('접속오류', e)
    finally:
        cur33.close()
        db33.close()


def savemultisetup(coinn, iniAsset, intRate, holdNo, userNo):
    db34 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur34 = db34.cursor()
    try:
        sql = "insert into assetCoins (userNo, coinName, initAsset, holdYN, intRate) values (%s,%s,%s,%s,%s)"
        cur34.execute(sql, (userNo, coinn, iniAsset, holdNo, intRate))
        db34.commit()
    except Exception as e:
        print('멀티트레이딩 설정오류', e)
    finally:
        cur34.close()
        db34.close()


def tradelog(uno,type,coinn,tstamp):
    global rows
    db35 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur35 = db35.cursor()
    try:
        if tstamp == "":
            tstamp = datetime.now()
        sql = "update tradeLog set attrib = %s where userNo = %s and tradeType = %s and coinName = %s"
        cur35.execute(sql, ("UPD00UPD00UPD00", uno, type, coinn))
        sql = "INSERT INTO tradeLog (userNo, tradeType, coinName, regDate) VALUES (%s, %s, %s, %s)"
        cur35.execute(sql,(uno, type, coinn, tstamp))
        db35.commit()
    except Exception as e:
        print('접속오류 트레이드 로그', e)
    finally:
        cur35.close()
        db35.close()


def cancelorder(uno,uuid):
    global rows
    db36 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur36 = db36.cursor()
    try:
        sql = "select apiKey1, apiKey2 from pondUser where userNo=%s"
        cur36.execute(sql, (uno))
        keys = cur36.fetchone()
        upbit = pyupbit.Upbit(keys[0], keys[1])
        upbit.cancel_order(uuid)
    except Exception as e:
        print("거래 취소 에러 ", e)
    finally:
        cur36.close()
        db36.close()


def gettop20():
    global rows
    db37 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur37 = db37.cursor()
    try:
        sql = "select * from trendcoins order by acc_trade_price desc limit 20"
        cur37.execute(sql)
        rows = cur37.fetchall()
    except Exception as e:
        print("추천코인 조회 에러 ", e)
    finally:
        cur37.close()
        db37.close()
        return rows


def resethotcoins():
    db38 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur38 = db38.cursor()
    try:
        sql = "update hotCoins set attrib = %s where attrib like %s"
        cur38.execute(sql, ("XXX00XXX00XXX00", "10000%"))
        db38.commit()
    except Exception as e:
        print("추천코인 리셋 에러",e)
    finally:
        cur38.close()
        db38.close()

def tradelist():
    global rows
    db39 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur39 = db39.cursor()
    try:
        sql = "select b.userName, a.*, c.setTitle, c.holdNo from tradingSetup a join pondUser b on a.userNo = b.userNo join tradingSets c on a.custKey = c.setNo where a.attrib = %s"
        cur39.execute(sql, "100001000010000")
        rows = cur39.fetchall()
    except Exception as e:
        print("투자 현황 조회 에러",e)
    finally:
        cur39.close()
        db39.close()
        return rows


def gettradelog(coinn, sdate, uno):
    global rows
    db39 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur39 = db39.cursor()
    try:
        sql = "select * from tradeLogDone where userNo = %s and market = %s and left(created_at,10) = %s"
        cur39.execute(sql, (uno, coinn, sdate))
        rows = cur39.fetchall()
    except Exception as e:
        print("거래이력 조회 에러 (request 방식) ",e)
    finally:
        cur39.close()
        db39.close()
        return rows


def tradedcoins(uno):
    global coins
    db40 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur40 = db40.cursor()
    try:
        sql = "select distinct bidCoin from tradingSetup where userNo=%s"
        cur40.execute(sql, (uno))
        coins = cur40.fetchall()
        coins = [list(coins[x]) for x in range(len(coins))]
    except Exception as e:
        print("거래 코인 목록 조회 에러 ", e)
    finally:
        cur40.close()
        db40.close()
        return coins


def modifyLog(uuid,stat):
    global rows
    db41 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur41 = db41.cursor()
    try:
        sql = "UPDATE tradeLogDetail set attrib = %s, mod_date = now() where uuid = %s"
        if stat == "canceled":
            stat = "CANC0CANC0CANC0"
        elif stat == "confirmed":
            stat = "CONF0CONF0CONF0"
        else:
            stat = "UPD00UPD00UPD00"
        cur41.execute(sql, (stat,uuid))
        db41.commit()
    except Exception as e:
        print('거래 기록 업데이트 에러',e)
    finally:
        cur41.close()
        db41.close()


def insertLog(uno,ldata01,ldata02,ldata03,ldata04,ldata05,ldata06,ldata07,ldata08,ldata09,ldata10,ldata11,ldata12,ldata13,ldata14,ldata15,ldata16):
    global rows
    db42 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur42 = db42.cursor()
    try:
        sql = ("insert into tradeLogDetail (userNo,orderDate,uuid,side,ord_type,price,market,created_at,volume,remaining_volume,reserved_fee,paid_fee,locked,executed_volume,excuted_funds,trades_count,time_in_force)"
               " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        cur42.execute(sql,(uno,ldata01,ldata02,ldata03,ldata04,ldata05,ldata06,ldata07,ldata08,ldata09,ldata10,ldata11,ldata12,ldata13,ldata14,ldata15,ldata16))
        db42.commit()
    except Exception as e:
        print("거래 기록 인서트 에러", e)
    finally:
        cur42.close()
        db42.close()


def getmytrlog(uno):
    global rows
    db43 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur43 = db43.cursor()
    try:
        sql = "select * from tradeLogDetail where userNo=%s and attrib != 'CANC0CANC0CANC0'"
        rows = cur43.execute(sql, (uno))
    except Exception as e:
        print("거래기록 조회 에러", e)
    finally:
        cur43.close()
        db43.close()
        return rows


def getmyincomes(uno):
    global rows
    db44 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur44 = db44.cursor()
    try:
        sql = "select * from incomeResult where userNo = %s order by tradeDate desc"
        cur44.execute(sql, uno)
        rows = cur44.fetchall()
    except Exception as e:
        print("수익 조회 에러",e)
    finally:
        cur44.close()
        db44.close()
        return rows


def mysettinglist(uno):
    global rows
    db45 = pymysql.connect(host=hostenv, user=userenv, password=passwordenv, db=dbenv, charset=charsetenv)
    cur45 = db45.cursor()
    try:
        sql = "select initAsset, bidInterval, doubleYN, left(max(regDate),10) as date from tradingSetup ts where userNo = %s and left(regDate ,10) >= DATE_ADD(now(), INTERVAL -2 month) group by left(regDate, 10)"
        cur45.execute(sql, (uno))
        rows = cur45.fetchall()
    except Exception as e:
        print("설정 조회 에러", e)
    finally:
        cur45.close()
        db45.close()
        return rows