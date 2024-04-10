import time
import comm.dbconn
import pyupbit
import math

bidcnt = 1


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


def buymarketpr(key1, key2, coinn, camount):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.buy_market_order(coinn, camount)
    return orders


def buylimitpr(key1, key2, coinn, setpr, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.buy_limit_order(coinn, setpr, setvol)
    return orders


def sellmarketpr(key1, key2, coinn, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.sell_market_order(coinn, setvol)
    return orders


def selllimitpr(key1, key2, coinn, setpr, setvol):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.sell_limit_order(coinn, setpr, setvol)
    return orders


def checktraded(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    checktrad = upbit.get_balances()
    for wallet in checktrad:
        if "KRW-" + wallet['currency'] == coinn:
            if float(wallet['balance']) != 0.0:
                print("잔고 남아 재거래")
            else:
                print('매도 거래 대기중')
            return wallet
        else:
            pass
    if checktrad is None:
        pass


def calprice(bidprice):
    if bidprice >= 2000000:
        bidprice = round(bidprice, -3)
    elif bidprice >= 1000000 and bidprice < 20000000:
        bidprice = round(bidprice, -3) + 500
    elif bidprice >= 500000 and bidprice < 1000000:
        bidprice = round(bidprice, -2)
    elif bidprice >= 100000 and bidprice < 500000:
        bidprice = round(bidprice, -2) + 50
    elif bidprice >= 10000 and bidprice < 100000:
        bidprice = round(bidprice, -1)
    elif bidprice >= 1000 and bidprice < 10000:
        bidprice = round(bidprice)
    elif bidprice >= 100 and bidprice < 1000:
        bidprice = round(bidprice, 1)
    elif bidprice >= 10 and bidprice < 100:
        bidprice = round(bidprice, 2)
    elif bidprice >= 1 and bidprice < 10:
        bidprice = round(bidprice, 3)
    else:
        bidprice = round(bidprice, 4)
    return bidprice


def cancelaskorder(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    for order in orders:
        print(order)
        if order['side'] == 'ask':
            upbit.cancel_order(order['uuid'])
            print("Canceled")


def canclebidorder(key1, key2, coinn):  #코인 청산
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    try:
        if orders is not None:
            for order in orders:
                upbit.cancel_order(order["uuid"])
        else:
            pass
    except Exception as e:
        print('cancel bid error',e)


def checkbidorder(key1, key2, coinn):
    upbit = pyupbit.Upbit(key1, key2)
    orders = upbit.get_order(coinn)
    for order in orders:
        if order['side'] == 'bid':
            return True
        else:
            return False


def runorders():
    setons = comm.dbconn.getsetonsvr(2)
    try:
        for seton in setons:  # 동록자별 동작 개시
            keys = getkeys(seton)  # 키로드
            myset = loadmyset(seton)  # 트레이딩 셋업로드
            orderstat = getorders(keys[0], keys[1], myset[6])  #주문현황 조회
            if myset[7] == 'Y':  #주문 ON 인 경우
                iniAsset = myset[2]  #기초 투입금액
                interVal = myset[3]  #매수 횟수
                intergap = myset[4]  #매수 간격
                intRate = myset[5]  #매수 이율
                coinn = myset[6]  #매수 종목
                preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
                traded = checktraded(keys[0], keys[1], coinn)  # 설정 코인 지갑내 존재 확인
                print(traded)
                if not orderstat:  #기존 주문내역이 없는 경우
                    print("기존 주문 없음")
                    if traded is None:  #지갑안에 해당 코인 없는 경우
                        canclebidorder(keys[0], keys[1], coinn)  #기존 매수 주문 취소
                        try:
                            bidasset = iniAsset
                            buyrest = buymarketpr(keys[0], keys[1], coinn, bidasset)  # 첫번째 설정 구매
                            print("시장가 구매", buyrest)
                            globals()['lcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
                        except Exception as e:
                            print(e)
                        finally:
                            print("1단계 매수내역 :", buyrest)
                        bidasset = iniAsset
                        # 추가 예약 매수 실행
                        for i in range(1, interVal + 1):
                            bidprice = ((preprice * 100) - (preprice * intergap * i)) / 100
                            bidprice = calprice(bidprice)
                            bidasset = bidasset * 2
                            bidvol = bidasset / bidprice
                            print('interval ', i, '예약 거래 적용')
                            print('매수가격', bidprice)
                            print('매수금액', bidasset)
                            print('매수수량', bidvol)
                            if globals()['lcnt_{}'.format(seton[0])] == 1:  # 구매 신호에 따라 구매 진행
                                buylimitpr(keys[0], keys[1], coinn, bidprice, bidvol)
                                print("매수 실행")
                            else:
                                print("매수 PASS")
                                pass
                        # 설정된 추가 매수 진행7
                        globals()['lcnt_{}'.format(seton[0])] = 2  # 구매 완료 설정
                    else:  #지갑에 해당 코인이 있는 경우
                        print("지갑내 자산 거래")
                        try:
                            setprice = preprice * (1.0 + (intRate / 100.0))
                            setprice = calprice(setprice)
                            setvolume = traded['balance']
                            selllimitpr(keys[0], keys[1], coinn, setprice, setvolume)
                            canclebidorder(keys[0], keys[1], coinn)  #기존 구매내역 취소
                            globals()['lcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
                            bidasset = iniAsset
                            # 추가 예약 매수만 실행
                            for i in range(1, interVal + 1):
                                bidprice = ((preprice * 100) - (preprice * intergap * i)) / 100
                                bidprice = calprice(bidprice)
                                bidasset = bidasset * 2
                                bidvol = bidasset / bidprice
                                print('interval ', i, '예약 거래 적용')
                                print('매수가격', bidprice)
                                print('매수금액', bidasset)
                                print('매수수량', bidvol)
                                if globals()['lcnt_{}'.format(seton[0])] == 1:  # 구매 신호에 따라 구매 진행
                                    buylimitpr(keys[0], keys[1], coinn, bidprice, bidvol)
                                    print("매수 실행")
                                else:
                                    print("매수 PASS")
                                    pass
                            # 설정된 추가 매수만 진행
                            globals()['lcnt_{}'.format(seton[0])] = 2  # 구매 완료 설정
                        except Exception as e:
                            print(e)
                        finally:
                            print("지갑에 코인이 있는 경우 완료")
                else:
                    print("기존 주문 존재")
                    if traded["balance"] != '0':
                        print("하락 매수로 인한 잔고 변동")
                        try:
                            cancelaskorder(keys[0], keys[1], coinn)  # 기존 매도 주문 취소
                            tradednew = checktraded(keys[0], keys[1], coinn)  # 설정 코인 지갑내 존재 확인
                            setprice = preprice * (1.005 + (intRate / 100.0))
                            setprice = calprice(setprice)
                            setvolume = tradednew['balance']
                            selllimitpr(keys[0], keys[1], coinn, setprice, setvolume)
                            #새로운 매도 주문
                        except Exception as e:
                            print(e)
                        finally:
                            print('매도주문 갱신')
                            # 새로운 주문 완료
                    else:
                        ordask = orderstat[0]["side"]
                        print(ordask)
                        if 'ask' in ordask:
                            print("전체금액 매도중")
                            globals()['lcnt_{}'.format(seton[0])] = 2  # 구매 완료 설정 - 변동 대기 모드
                        else:
                            canclebidorder(keys[0], keys[1], coinn)  #구매예약 취소
                            globals()['bcnt_{}'.format(seton[0])] = 0  # 점검횟수 초기화
                globals()['bcnt_{}'.format(seton[0])] += 1  # 점검횟수 증가
                print(globals()['bcnt_{}'.format(seton[0])])  #횟수 체크
            else:
                print("거래 중지중(N)", seton[0])
                myset = loadmyset(seton[0])
                coinn = myset[6]
                canclebidorder(keys[0], keys[1], coinn)
                print('-----------------------')
                globals()['lcnt_{}'.format(seton[0])] = 0
                globals()['bcnt_{}'.format(seton[0])] = 0  # 점검횟수 초기화
                print(globals()['bcnt_{}'.format(seton[0])])  #횟수 체크
    except Exception as e:
        print(e)
    comm.dbconn.clearcache()  # 캐쉬 삭제


def order_cnt_trade():
    global orderstat, key1, key2, coinn, askcnt, bidcnt, traded
    setons = comm.dbconn.getsetonsvr(1)  #서버별 사용자 로드
    try:
        for seton in setons:
            keys = getkeys(seton)
            key1 = keys[0]  # 키로드
            key2 = keys[1]  # 키로드
            myset = loadmyset(seton)  # 트레이딩 셋업로드
            iniAsset = myset[2]  # 기초 투입금액
            interVal = myset[3]  # 매수 횟수
            intergap = myset[4]  # 매수 간격
            intRate = myset[5]  # 매수 이율
            coinn = myset[6]  # 매수 종목
            if myset[7] == 'Y':  # 주문 ON 인 경우
                print('주문 개시')
                preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
                orderstat = getorders(keys[0], keys[1], myset[6])  # 주문현황 조회
                if globals()['tcnt_{}'.format(seton[0])] == 0:  #거래단계 처음
                    traded = checktraded(keys[0], keys[1], coinn)  # 설정 코인 지갑내 존재 확인
                    if traded is None:
                        print('최초 거래 시작')
                        order_new_bid(keys[0], keys[1], coinn, iniAsset, interVal, intergap, intRate)
                    else:
                        print('지갑에 코인 존재')
                        bidcnt = 0
                        askcnt = 0
                        orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                        if orderstat is None: #주문 없을때
                            print('지갑에 코인을 정리해 주세요')
                            break
                        else:
                            for order in orderstat:
                                if order['side'] == 'bid':
                                    bidcnt += 1
                                elif order['side'] == 'ask':
                                    askcnt += 1
                            globals()['askcnt_{}'.format(seton[0])] = askcnt  # 매수거래 수 확인
                            globals()['bidcnt_{}'.format(seton[0])] = bidcnt  # 매도거래 수 확인
                            globals()['tcnt_{}'.format(seton[0])] = 2  # 확인 단계로 진행
                            print('ask 수', globals()['askcnt_{}'.format(seton[0])])
                            print('bid 수', globals()['bidcnt_{}'.format(seton[0])])
                elif globals()['tcnt_{}'.format(seton[0])] == 1:
                    print('1단계 거래') # 주문 카운트
                    bidcnt1 =0
                    askcnt1 =0
                    orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                    print('주문현황', orderstat)
                    for order in orderstat:
                        if order['side'] == 'bid':
                            bidcnt1 += 1
                        elif order['side'] == 'ask':
                            askcnt1 += 1
                        #주문 확인 후 2단계로
                        globals()['askcnt_{}'.format(seton[0])] = askcnt1  # 매수거래 수 확인
                        globals()['bidcnt_{}'.format(seton[0])] = bidcnt1  # 매도거래 수 확인
                        globals()['tcnt_{}'.format(seton[0])] = 2  # 확인 단계로 진행
                elif globals()['tcnt_{}'.format(seton[0])] == 2:
                    print('2단계 거래')
                    bidcnt2 = 0
                    askcnt2 = 0
                    # 매수거래 카운트
                    orderstat = getorders(key1, key2, coinn)  # 주문현황 조회
                    for order in orderstat:
                        if order['side'] == 'bid':
                            bidcnt2 += 1
                        elif order['side'] == 'ask':
                            askcnt2 += 1
                    print('bidcnt2', bidcnt2)
                    print('globbidcnt', globals()['bidcnt_{}'.format(seton[0])])
                    print('askcnt2', askcnt2)
                    print('globbidcnt', globals()['askcnt_{}'.format(seton[0])])
                    if bidcnt2 != globals()['bidcnt_{}'.format(seton[0])]:
                        print('bidcnt2', bidcnt2)
                        print('globbidcnt', globals()['bidcnt_{}'.format(seton[0])])
                        #거래수 다를시 재설정
                        print('추가 매수에 의한 재설정')
                        order_mod_ask(keys[0], keys[1], coinn, intRate)
                        globals()['tcnt_{}'.format(seton[0])] = 1  # 거래단계 초기화
                    elif askcnt2 == 0:  # 전체 거래 취소 후 재구매
                        print('매도 완료에 따른 재 설정', askcnt2)
                        canclebidorder(key1, key2, coinn)
                        globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
                else:
                    print('나머지 단계 거래')
                chkcoin = checktraded(key1, key2, coinn)  # 지갑 점검
                if chkcoin is None: # 지갑내 해당코인이 없을 경우
                    canclebidorder(key1, key2, coinn) # 주문 취소
                    globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
            else:
                print('주문 대기 user', seton[0])
                globals()['tcnt_{}'.format(seton[0])] = 0  # 거래단계 초기화
                canclebidorder(key1, key2, coinn)
                print('-----------------------')
    except Exception as e:
        print('level 1 Error :', e)
    finally:
        print('거래점검 완료', cnt)
        comm.dbconn.clearcache()  # 캐쉬 삭제


def order_new_bid(key1, key2, coinn, initAsset, intval, intergap, profit):
    global buyrest, bidasset, bidcnt, askcnt
    print("새로운 주문 함수 실행")
    preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
    try:
        bidasset = initAsset
        buyrest = buymarketpr(key1, key2, coinn, bidasset)  # 첫번째 설정 구매
        print("시장가 구매", buyrest)
        globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 함으로 설정
    except Exception as e:
        print(e)
    finally:
        print("1단계 매수내역 :", buyrest)
        traded = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.0 + (profit / 100.0))
        setprice = calprice(setprice)
        setvolume = traded['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume)
    # 추가 예약 매수 실행
    for i in range(1, intval + 1):
        bidprice = ((preprice * 100) - (preprice * intergap * i)) / 100
        bidprice = calprice(bidprice)
        bidasset = bidasset * 2
        bidvol = bidasset / bidprice
        print('interval ', i, '예약 거래 적용')
        print('매수가격', bidprice)
        print('매수금액', bidasset)
        print('매수수량', bidvol)
        if globals()['tcnt_{}'.format(seton[0])] == 1:  # 구매 신호에 따라 구매 진행
            buylimitpr(key1, key2, coinn, bidprice, bidvol)
            print("매수 실행")
        else:
            print("매수 PASS")
    # 설정된 추가 매수 진행
    globals()['tcnt_{}'.format(seton[0])] = 1  # 구매 완료 설정
    #주문 개수 확인
    return None


def order_mod_ask(key1, key2, coinn, profit):
    print("매도 주문 재생성")
    try:
        preprice = pyupbit.get_current_price(coinn)  # 현재값 로드
        cancelaskorder(key1, key2, coinn)  # 기존 매도 주문 취소
        tradednew = checktraded(key1, key2, coinn)  # 설정 코인 지갑내 존재 확인
        setprice = preprice * (1.005 + (profit / 100.0))
        setprice = calprice(setprice)
        setvolume = tradednew['balance']
        selllimitpr(key1, key2, coinn, setprice, setvolume)
        # 새로운 매도 주문
    except Exception as e:
        print('매도주문 갱신 에러 ',e)
    finally:
        print('매도주문 갱신')
        globals()['tcnt_{}'.format(seton[0])] = 3  # 구매 완료 설정
        # 새로운 주문 완료
    return None


cnt = 1
setons = comm.dbconn.getseton()
for seton in setons:
    globals()['lcnt_{}'.format(seton[0])] = 0  #거래단계 초기화
    globals()['bcnt_{}'.format(seton[0])] = 0  #점검횟수 초기화
    globals()['tcnt_{}'.format(seton[0])] = 0  # 거래 예약 횟수 초기화
    globals()['askcnt_{}'.format(seton[0])] = 0  # 매도거래 수
    globals()['bidcnt_{}'.format(seton[0])] = 0  # 매수거래 수

while True:
    print("Run Count : ", cnt)
    try:
        order_cnt_trade()
        cnt = cnt + 1
    except Exception as e:
        print(e)
    finally:
        time.sleep(1.5)
