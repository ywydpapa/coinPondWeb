import pyupbit
import time
from datetime import datetime
import pymysql
import random

db = pymysql.connect(host='swc9004.iptime.org', user='swc', password='core2020', db='anteUpbit')
cur = db.cursor()


while True:
    try:
        cur = db.cursor()
        sql = "select * from tradingSetup where attrib not like %s"
        cur.execute(sql, '%XXXUP')
        data = list(cur.fetchall())
        for dd in data:
            print(dd)
        print("다른거 조회")
        sql = "select * from setons"
        cur.execute(sql)
        data = list(cur.fetchall())
        for dd in data:
            print(dd)
        sql = "RESET QUERY CACHE"
        cur.execute(sql)
        cur.close()
        data = None
    except Exception as e:
        print('접속오류', e)
    finally:
        print("RESET")

    time.sleep(10)