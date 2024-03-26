import time
import comm.dbconn
import pyupbit
import math


def loadmyset(uno):
    mysett = comm.dbconn.getsetups(uno)
    return mysett


def getkeys(uno):
    mykey = comm.dbconn.getupbitkey(uno)
    return mykey


def getorders(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    return orders


def liqcoin(key1, key2, coinn): #코인 청산
    upbit = pyupbit.Upbit(key1,key2)
    orders = upbit.get_order(coinn)
    if len(orders)>0:
        for order in orders:
            upbit.cancel_order(order["uuid"])
    else:
        pass


def buymarketpr(key1, key2, coinn, camount):
    upbit = pyupbit.Upbit(key1,key2)
    orders = upbit.buy_market_order(coinn, camount)
    return orders


def buylimitpr(key1, key2, coinn, setpr, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.buy_limit_order(coinn,setpr,setvol)
    return orders


def sellmarketpr(key1, key2, coinn, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.sell_market_order(coinn,setvol)
    return orders



def runorders():
    setons = comm.dbconn.getseton()
    if setons is not None:
        for seton in setons:
            keys = getkeys(seton)
            myset = loadmyset(seton)
            items = getorders(keys[0], keys[1], myset[6])
            if myset[7] == 'Y': #거래 개시인 것만
                iniAsset = myset[2]
                interVal = myset[3]
                intergap = myset[4]
                interestRate = myset[5]
                coinn = myset[6]
                preprice = pyupbit.get_current_price(coinn)
                print('현재가', preprice)
                bidasset = iniAsset
                for i in range(1,interVal+1):
                    bidprice = ((preprice * 100) - (preprice * intergap*i)) / 100
                    if bidprice >= 2000000 :
                        bidprice = round(bidprice,-3)
                    elif bidprice >= 1000000 and bidprice < 20000000:
                        bidprice = round(bidprice, -3) + 500
                    elif bidprice >=500000 and bidprice < 1000000:
                        bidprice = round(bidprice, -2)
                    elif bidprice >=100000 and bidprice < 500000:
                        bidprice = round(bidprice, -2) + 50
                    elif bidprice >=10000 and bidprice < 100000:
                        bidprice = round(bidprice, -1)
                    elif bidprice >=1000 and bidprice < 10000:
                        bidprice = round(bidprice)
                    elif bidprice >= 100 and bidprice < 1000:
                        bidprice = round(bidprice,1)
                    elif bidprice >= 10 and bidprice < 100:
                        bidprice = round(bidprice,2)
                    elif bidprice >= 1 and bidprice < 10:
                        bidprice = round(bidprice,3)
                    else:
                        bidprice = round(bidprice,4)
                    bidasset = bidasset * 2
                    bidvol = bidasset / bidprice
                    print('interval ',i,'예약 거래 적용')
                    print('매수가격',bidprice)
                    print('매수금액',bidasset)
                    print('매수수량',bidvol)
                print('거래 개시')
            else:#거래 대기 상태
                print("거래 대기")
    else:
        print("No seton found!!")
    comm.dbconn.clearcache()


cnt = 1

while True:
    print("Count : ", cnt)
    runorders()
    cnt = cnt+1
    time.sleep(10)
