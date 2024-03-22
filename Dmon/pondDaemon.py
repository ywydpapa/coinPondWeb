import time
import comm.dbconn
import pyupbit

def loadmyset(uno):
    myset = comm.dbconn.getsetup(uno)
    return myset

def getkeys(uno):
    mykey = comm.dbconn.getupbitkey(uno)
    return mykey

def getorders(key1,key2,coinn):
    upbit = pyupbit.Upbit(key1,key2)
    orders = upbit.get_order(coinn)
    return orders

def runorders():
    setons = comm.dbconn.getseton()
    if setons != None:
        for seton in setons:
            keys = getkeys(seton)
            myset = loadmyset(seton)
            items = getorders(keys[0], keys[1], myset[0])
            if myset is not None:
                print(myset)
                print(items)
            else:
                print("No seton found!")
    else:
        print("No seton found!!")

cnt = 1

while True:
    print("Count : ", cnt)
    runorders()
    cnt = cnt+1
    time.sleep(5)
