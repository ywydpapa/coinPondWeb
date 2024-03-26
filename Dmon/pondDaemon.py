import time
import comm.dbconn
import pyupbit


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


def runorders():
    setons = comm.dbconn.getseton()
    if setons is not None:
        for seton in setons:
            keys = getkeys(seton)
            myset = loadmyset(seton)
            items = getorders(keys[0], keys[1], myset[6])
            print(myset)
            if myset[7] == 'Y':
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
                    bidasset = bidasset * 2
                    print('interval ',i,'예약 거래 적용')
                    print('매수가격',bidprice)
                    print('매수금액',bidasset)
                print('거래 개시')
            else:
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
