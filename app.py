import time
from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import (selectUsers, setKeys, checkwallet, tradehistory, hotcoinlist, setupbid, getsetup, setonoff, \
                         checkwalletwon, getorderlist, listUsers, detailuser, setupbidadmin, selectsets,
                         setdetail, selectsetlist, \
                         setmypasswd, updateuserdetail, updatebidadmin, settingonoff, hotcoinlist, sethotcoin,
                         selectboardlist, boarddetail, resethotcoins, setLog, \
                         boardupdate, boardnewwrite, setholdreset, getmessage, cancelorder, gettop20, tradehistorys,
                         servicestatus,
                         tradelist, readmsg, gettradelog, tradedcoins, modifyLog, insertLog, getmytrlog, getmyincomes,
                         checkwalletremains,
                         mysettinglist, getsetupmax, erasebid, getsetups, setonoffs, editbidsetup, getlicence,
                         mytradesetlist, setallonoff, custlist, custdetail, insertcust, changesvr, getsetupitem,
                         sellmycoinpercent)
from comm.upbitdata import dashcandle548, get_ticker_tradevalue, dashcandle160
import pyupbit
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
Bootstrap(app)


@app.route('/')
def home():  # put application's code here
    return render_template('./login/login.html')


@app.route('/dashboard')
def dashboard():
    noticelist = selectboardlist(0) #공지사항 조회
    boarditems = selectboardlist(1)
    btccand = [dashcandle548("KRW-BTC")]
    ethcand = [dashcandle548("KRW-ETH")]
    xrpcand = [dashcandle548("KRW-XRP")]
    indexv = btccand[0].index.tolist()
    listbtc = btccand[0]['open'].tolist()
    listeth = ethcand[0]['open'].tolist()
    listxrp = xrpcand[0]['open'].tolist()
    listbtcc = btccand[0]['close'].tolist()
    listethc = ethcand[0]['close'].tolist()
    listxrpc = xrpcand[0]['close'].tolist()
    return render_template('./trade/dashboard.html', btccands=listbtc, ethcands=listeth,xrpcands=listxrp, btccandsc=listbtcc, ethcandsc=listethc,xrpcandsc=listxrpc, indexv=indexv, noticelist=noticelist, boarditem=boarditems)


@app.route('/trade', methods=['GET', 'POST'])
def trade():
    global avprice,avprice2,avprice3
    uno = request.args.get('uno')
    setkey = request.args.get('skey')
    tabindex = request.args.get('tabindex')
    license = getlicence(uno)[0]
    setups = getsetups(uno,tabindex)
    wallet = checkwalletwon(uno, setkey)
    orderlist = getorderlist(uno, tabindex)
    setno1 = setups[0][8]
    setno2 = setups[1][8]
    setno3 = setups[2][8]
    trset1 = setdetail(setno1)
    trset2 = setdetail(setno2)
    trset3 = setdetail(setno3)
    coinn1 = setups[0][6]
    coinn2 = setups[1][6]
    coinn3 = setups[2][6]
    crprice1 = pyupbit.get_current_price(coinn1)
    crprice2 = pyupbit.get_current_price(coinn2)
    crprice3 = pyupbit.get_current_price(coinn3)
    wallets = checkwallet(uno, setkey)
    avprice1 = 0
    avprice2 = 0
    avprice3 = 0
    srate1 = 0
    srate2 = 0
    srate3 = 0
    for wallett in wallets:
        if "KRW-"+wallett["currency"] == coinn1:
            avprice1 = wallett["avg_buy_price"]
            if float(avprice1) <= 0:
                avprice1 = 0
        elif "KRW-"+wallett["currency"] == coinn2:
            avprice2 = wallett["avg_buy_price"]
            if float(avprice2) <= 0:
                avprice2 = 0
        elif "KRW-"+wallett["currency"] == coinn3:
            avprice3 = wallett["avg_buy_price"]
            if float(avprice3) <= 0:
                avprice3 = 0
    if float(avprice1) > 0:
        srate1 = round(float(crprice1)/float(avprice1)*100,4)
    if float(avprice2) > 0:
        srate2 = round(float(crprice2)/float(avprice2)*100,4)
    if float(avprice3) > 0:
        srate3 = round(float(crprice3)/float(avprice3)*100,4)
    coincand1 = [dashcandle160(coinn1)]
    listcoino1 = coincand1[0]['open'].tolist()
    listcoinc1 = coincand1[0]['close'].tolist()
    coincand2 = [dashcandle160(coinn2)]
    listcoino2 = coincand2[0]['open'].tolist()
    listcoinc2 = coincand2[0]['close'].tolist()
    coincand3 = [dashcandle160(coinn3)]
    listcoino3 = coincand3[0]['open'].tolist()
    listcoinc3 = coincand3[0]['close'].tolist()
    return render_template('./trade/mytrademain.html', wallet=wallet, list=orderlist, trset1=trset1,trset2=trset2,trset3=trset3,
                           coinopen1 = listcoino1, coinclose1 = listcoinc1, cprice1 = crprice1, bsrate1 = srate1,
                           coinopen2 = listcoino2, coinclose2 = listcoinc2, cprice2 = crprice2, bsrate2 = srate2,
                           coinopen3 = listcoino3, coinclose3 = listcoinc3, cprice3 = crprice3, bsrate3 = srate3,
                           avprice1 = avprice1,avprice2 = avprice2,avprice3 = avprice3, setups = setups, tabindex = tabindex, license = license)


@app.route('/tradeSet', methods=['GET', 'POST'])
def tradeSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    coinn = request.args.get('coinn')
    uno = request.args.get('uno')
    trcnt = getlicence(uno)[0]
    setlist = selectsetlist(9)
    print(setlist)
    return render_template('./trade/setmytrade.html', coinlist=coinlist, coinn=coinn, setlist=setlist, trcnt=trcnt)


@app.route('/editSetup', methods=['GET', 'POST'])
def editSetup():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    setno = request.args.get('setno')
    coinA = request.args.get('coinA')
    coinB = request.args.get('coinB')
    tabindex = request.args.get('tabindex')
    setlist = selectsetlist(9)
    print(setlist)
    return render_template('./trade/editmytrade.html', coinlist=coinlist, setno=setno, coinA=coinA, coinB= coinB, setlist=setlist, tabindex=tabindex)

@app.route('/multisetup', methods=['GET', 'POST'])
def multisetup():
    coinlist = hotcoinlist()
    print(coinlist)
    coinn = request.args.get('coinn')
    setlist = selectsetlist(9)
    return render_template('./trade/setmultitrade.html', coinlist=coinlist, coinn=coinn, setlist=setlist)


@app.route('/tradeSet2', methods=['GET', 'POST'])
def tradeSet2():
    coinlist = hotcoinlist()
    coinn = request.args.get('coinn')
    setlist = selectsetlist(9)
    return render_template('./trade/setmytrade2.html', coinlist=coinlist, coinn=coinn, setlist=setlist)


@app.route('/adminSet', methods=['GET', 'POST'])
def adminSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    coinn = request.args.get('coinn')
    return render_template('./admin/adminsetup.html', coinlist=coinlist, coinn=coinn)


@app.route('/peakcoin', methods=['GET', 'POST'])
def peakcoin():
    hotcoins = hotcoinlist()
    return render_template('./trade/hotcoins.html', hotcoins=hotcoins)


@app.route('/volumetop20', methods=['GET', 'POST'])
def volumetop20():
    trendcoins = gettop20()
    return render_template('./trade/top20.html', trendcoins=trendcoins)


@app.route('/coincollect', methods=['GET', 'POST'])
def coincollect():
    uno = request.args.get('uno')
    skey = request.args.get('skey')
    coinn = request.args.get('coinn')
    setLog(uno, skey, coinn)
    path="/coindetails?uno="+uno+"&skey="+skey+"&coinn="+coinn;
    return redirect(path)


@app.route('/coindetail', methods=['GET', 'POST'])
def coindetail():
    uno = request.args.get('uno')
    skey = request.args.get('skey')
    coinlist = pyupbit.get_tickers(fiat="KRW")
    trcoinlist = tradedcoins(uno)
    orderlist = tradehistory(uno, skey) #거래 일자만 검색
    trdate = []
    for order in orderlist:
        trdate.append(order["created_at"][0:10])
    trdate = set(trdate)
    trdate = list(trdate)
    sdate = datetime.strftime(datetime.today(), '%Y-%m-%d')
    mysetrate = getsetup(uno)
    setcoin = getsetup(uno)[0]
    try:
        orderlist2 = gettradelog(setcoin, sdate, uno)
        print(orderlist2)
        if orderlist2 is None:
            orderlist2 = []
    except Exception as e:
        orderlist2 = []
    trdate = sorted(trdate, reverse=True)
    return render_template('./trade/mytraderesult.html', orderlist=trdate, myset = mysetrate, coinlist =coinlist, setcoin0 = setcoin, sdate = sdate, reqitems = orderlist2, trcoinlist = trcoinlist)


@app.route('/traderesult', methods=['GET', 'POST'])
def traderesult():
    uno = request.args.get('uno')
    sdate = datetime.strftime(datetime.today(), '%Y-%m-%d')
    mysetrate = getsetup(uno)
    setcoin = getsetup(uno)[0]
    try:
        incomes = getmyincomes(uno)
    except Exception as e:
        incomes = []
    return render_template('./trade/mytradeearning.html', myset = mysetrate, setcoin0 = setcoin, sdate = sdate, incomes = incomes)


@app.route('/coindetails', methods=['GET', 'POST'])
def coindetails():
    global trdate
    uno = request.args.get('uno')
    skey = request.args.get('skey')
    coinn = request.args.get('coinn')
    sdate = request.args.get('sdate')
    trcoinlist = tradedcoins(uno)
    coinlist = pyupbit.get_tickers(fiat="KRW")
    try:
        orderlist = tradehistorys(uno, skey, coinn)
        trdate = []
        for order in orderlist:
            trdate.append(order["created_at"][0:10])
        trdate = set(trdate)
        trdate = list(trdate)
        if orderlist is None:
            orderlist = []
    except Exception as e:
        orderlist = []
    mysetrate = getsetupmax(uno, sdate)
    setcoin = coinn
    try:
        orderlist2 = gettradelog(setcoin, sdate, uno)
        if orderlist2 is None:
            orderlist2 = []
    except Exception as e:
        orderlist2 = []
    trdate = sorted(trdate, reverse=True)
    return render_template('./trade/mytraderesult.html', orderlist=trdate, myset = mysetrate, coinlist = coinlist, setcoin0 = setcoin, sdate = sdate, reqitems = orderlist2, trcoinlist = trcoinlist)


@app.route('/tradestat', methods=['GET', 'POST'])
def tradestat():
    if request.method == "POST":
        return render_template('trade/tradestat.html')
    else:
        mycoins = []
        uno = request.args.get('uno')
        skey = request.args.get('skey')
        walletitems = checkwallet(uno, skey)
        mysetcoins = getsetups(uno,0)
        myset = []
        for mysetcoin in mysetcoins:
            myset.append(mysetcoin[6])
        for wallet in walletitems:
            if wallet['currency'] != "KRW":
                ccoin = "KRW-" + wallet['currency']
                try:
                    cpr = pyupbit.get_current_price(ccoin)
                    time.sleep(0.2)
                except Exception as e:
                    cpr = 1
                curr = [wallet['currency'], cpr]
                mycoins.append(curr)
        return render_template('./trade/mywallet.html', witems=walletitems, mycoins=mycoins, mysetcoin =myset)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global uno, svrno, skey, path
    if request.method == 'GET':
        return render_template('./login/login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        row = selectUsers(uid, upw)
        if row is not None:
            try:
                session['userNo'] = row[0][0]
                session['userName'] = row[0][1]
                session['serverNo'] = row[0][2]
                session['userRole'] = row[0][3]
                session['setkey'] = str(row[1])
                uno = row[0][0]
                skey = str(row[1])
                svrno = row[0][2]
                setKeys(uno, skey)
                path = '/dashboard'
                #path = '/t1rade?uno=' + str(uno) + '&skey=' + str(skey) + '&svrno=' + str(svrno)
            except Exception as e:
                session['userNo'] = 0
                session['userName'] = '브라우저 재시작 필요'
                session['serverNo'] = 0
                session['setkey'] = '000000'
                print(e)
                path = '/login'
            finally:
                return redirect(path)
        else:
            return '''
                <script>
                    // 경고창 
                    alert("로그인 실패, 다시 시도하세요");
                    // 이전페이지로 이동
                    history.back();
                </script>
            '''


@app.route('/setupbid', methods=['GET', 'POST'])
def setupmybid():
    global skey, uno, slot
    if request.method == 'GET':
        pass
    else:
        uno = request.form.get('userno')
        slot = request.form.get('tabindex')
        bidsetps = request.form.get('bidsteps')
        initprice = request.form.get('initprice')
        initprice = initprice.replace(',', '')
        bidrate = 1.00
        initprice = initprice.replace(',', '')
        askrate = 0.5
        tradeset = request.form.get('tradeset')
        tradeset = tradeset.split(',')[0]
        coinn1 = request.form.get('coinn1')
        coinn2 = request.form.get('coinn2')
        coinn3 = request.form.get('coinn3')
        skey = request.form.get('skey')
        svrno = request.form.get('svrno')
        hno = request.form.get('tradeset').split(',')[1]
        dyn = request.form.get('doublechk')
        lmtamt = request.form.get('limitamt')
        lmtamt = lmtamt.replace(',', '')
        if dyn == 'ON':
            dyn = 'Y'
        else:
            dyn = 'N'
        erasebid(uno,skey, slot)
        if coinn1 is not None:
            setupbid(uno, skey, initprice, bidsetps, bidrate, askrate, coinn1, svrno, tradeset, hno, dyn, lmtamt, slot)
        if coinn2 is not None:
            setupbid(uno, skey, initprice, bidsetps, bidrate, askrate, coinn2, svrno, tradeset, hno, dyn, lmtamt, slot)
        if coinn3 is not None:
            setupbid(uno, skey, initprice, bidsetps, bidrate, askrate, coinn3, svrno, tradeset, hno, dyn, lmtamt, slot)
    return redirect('/trade?uno=' + uno + '&skey=' + skey + '&tabindex=' + slot )


@app.route('/setupbid2', methods=['GET', 'POST'])
def editmybid2():
    if request.method == 'GET':
        pass
    else:
        setno = request.form.get('sno')
        uno = request.form.get('userno')
        slot = request.form.get('tabindex')
        bidsetps = request.form.get('bidsteps')
        initprice = request.form.get('initprice')
        initprice = initprice.replace(',', '')
        bidrate = 1.00
        initprice = initprice.replace(',', '')
        askrate = 0.5
        tradeset = request.form.get('tradeset')
        tradeset = tradeset.split(',')[0]
        coinn = request.form.get('coinn')
        skey = request.form.get('skey')
        svrno = request.form.get('svrno')
        hno = request.form.get('tradeset').split(',')[1]
        dyn = request.form.get('doublechk')
        limityn = request.form.get('limityn')
        limitamt = request.form.get('limitamt')
        limitamt = limitamt.replace(',', '')
        if dyn == 'ON':
            dyn = 'Y'
        else:
            dyn = 'N'
        if coinn is not None:
            editbidsetup(setno, uno, skey, initprice, bidsetps, bidrate, askrate, coinn, svrno, tradeset, hno, dyn, limityn, limitamt, slot)
    return redirect('/trade?uno=' + uno + '&skey=' + skey + '&tabindex=' + slot)


@app.route('/setupbidadmin', methods=['GET', 'POST'])
def setupmybidadmin():
    global skey, uno
    if request.method == 'GET':
        pass
    else:
        uno = request.form.get('userno')
        bidsteps = request.form.get('bidsteps')
        settitle = request.form.get('settitle')
        skey = request.form.get('skey')
        svrno = request.form.get('svrno')
        g0 = request.form.get('steprate')
        g1 = request.form.get('gap01')
        g2 = request.form.get('gap02')
        g3 = request.form.get('gap03')
        g4 = request.form.get('gap04')
        g5 = request.form.get('gap05')
        g6 = request.form.get('gap06')
        if int(bidsteps) >= 7:
            g7 = request.form.get('gap07')
        else:
            g7 = g6
        if int(bidsteps) >= 8:
            g8 = request.form.get('gap08')
        else:
            g8 = g7
        if int(bidsteps) >= 9:
            g9 = request.form.get('gap09')
        else:
            g9 = g8
        r0 = request.form.get('profitrate')
        r1 = request.form.get('int01')
        r2 = request.form.get('int02')
        r3 = request.form.get('int03')
        r4 = request.form.get('int04')
        r5 = request.form.get('int05')
        r6 = request.form.get('int06')
        r7 = request.form.get('int07')
        r8 = request.form.get('int08')
        r9 = request.form.get('int09')
        hyn = request.form.get('holdon')
        dyn = request.form.get('doublechk')
        if dyn == 'on':
            dyn = 'Y'
        else:
            dyn = 'N'
        setupbidadmin(uno, skey, settitle, bidsteps, g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, hyn, dyn)
    return redirect('/setlist')


@app.route('/setlist', methods=['GET', 'POST'])
def setlist():
    global rows
    rows = selectsets()
    return render_template('./admin/setlistn.html', rows = rows)

@app.route('/tradesetlist', methods=['GET', 'POST'])
def tradesetlist():
    global rows
    uno = request.args.get('uno')
    rows = mytradesetlist(uno)
    return render_template('./trade/mysettinglist.html', rows = rows)

@app.route('/setDetail', methods=['GET', 'POST'])
def detailset():
    global rows
    sno = request.args.get('setno')
    rows = setdetail(sno)
    print(rows)
    return render_template('./admin/setdetailn.html', rows = rows)


@app.route('/logout')
def logout():
    session.clear()
    return render_template('./login/login.html')


@app.route('/userAdmin')
def useradmin():
    users = listUsers()
    return render_template('./admin/useradminn.html', users=users)


@app.route('/userDetail')
def userdetail():
    userno = request.args.get('uno')
    user = detailuser(userno)
    return render_template('./admin/userDetailn.html', user=user)


@app.route('/custAdmin')
def custadmin():
    custs = custlist()
    return render_template('./admin/custadmin.html', custs=custs)


@app.route('/custDetail')
def cstdetail():
    custno = request.args.get('custno')
    cust = custdetail(custno)
    return render_template('./admin/custDetail.html', cust=cust)


@app.route('/updatecust', methods=['GET', 'POST'])
def updatecust():
    if request.method == 'GET':
        pass
    else:
        custno = request.args.get('custno')
    return redirect("./custAdmin")


@app.route('/changemySet')
def mydetail():
    userno = request.args.get('uno')
    user = detailuser(userno)
    return render_template('./trade/mysettings.html', user=user)


@app.route('/setyn', methods=['POST'])
def setyn():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    yesno = pla[1]
    setonoff(uno, yesno)
    return "YES"


@app.route('/setallyn', methods=['POST'])
def setallyn():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    yesno = pla[1]
    setallonoff(uno, yesno)
    return "YES"


@app.route('/setyns', methods=['POST'])
def setyns():
    pla = request.get_data().decode('utf-8').split(',')
    setno = pla[0]
    yesno = pla[1]
    item = getsetupitem(setno)
    # 지갑 조회 후 설정 리턴
    mybal = checkwalletremains(item[0], item[1])
    wallvalue = float(mybal[0])*float(mybal[1])
    if wallvalue > 100000:
        if yesno == 'Y':
            return "OVER"
        else:
            setonoffs(setno, yesno)
            return "YES"
    else:
        setonoffs(setno, yesno)
        return "YES"


@app.route('/sethr', methods=['POST'])
def sethr():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    hldrst = pla[1]
    print(uno)
    print(hldrst)
    setholdreset(uno,hldrst)
    return "YES"


@app.route('/hotyn', methods=['POST'])
def hotyn():
    pla = request.get_data().decode('utf-8').split(',')
    coinn = pla[0]
    yesno = pla[1]
    print(coinn)
    print(yesno)
    sethotcoin(coinn, yesno)
    return "YES"


@app.route('/resethotyn', methods=['POST'])
def resethotyn():
    resethotcoins()
    return "YES"


@app.route('/settingyn', methods=['POST'])
def settingyn():
    pla = request.get_data().decode('utf-8').split(',')
    sno = pla[0]
    yesno = pla[1]
    settingonoff(sno, yesno)
    return "YES"


@app.route('/changemypass', methods=['POST'])
def changemypass():
    passwd = request.get_data().decode('utf-8').split(',')
    uno = passwd[0]
    passwd = passwd[1]
    setmypasswd(uno, passwd)
    return "YES"


@app.route('/updateuser', methods=['POST'])
def updateuser():
    uno = request.form.get('uno')
    key1 = request.form.get('apikey1')
    key2 = request.form.get('apikey2')
    svrno = request.form.get('svrno')
    updateuserdetail(uno, key1, key2, svrno)
    users = listUsers()
    return render_template('./admin/useradminn.html', users=users)


@app.route('/updatemyuser', methods=['POST'])
def updatemyuser():
    uno = request.form.get('uno')
    key1 = request.form.get('apikey1')
    key2 = request.form.get('apikey2')
    svrno = request.form.get('svrno')
    updateuserdetail(uno, key1, key2, svrno)
    changesvr(uno, svrno)
    users = listUsers()
    return render_template('./trade/dashboard.html', users=users)


@app.route('/sellcoin', methods=['POST'])
def sellcoin():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    coinn = "KRW-"+pla[1]
    rate = pla[2]
    sellmycoinpercent(uno, coinn, rate)
    return "YES"


@app.route('/cancelOrder', methods=['POST'])
def cancorder():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    uuid = pla[1]
    cancelorder(uno,uuid)
    modifyLog(uuid, "canceled")
    return "YES"


@app.route('/hotcoins')
def hotcoins():
    tickers = pyupbit.get_tickers(fiat="KRW")
    coindtl = pyupbit.get_orderbook(ticker=tickers)
    trval = get_ticker_tradevalue() # 코인 거래금액 추가
    return render_template('./admin/hotcoinsn.html', coinlist=tickers, coindtls = coindtl, trval = trval)


@app.route('/hotcoinsm')
def hotcoinsm():
    tickers = pyupbit.get_tickers(fiat="KRW")
    coindtl = pyupbit.get_orderbook(ticker=tickers)
    trval = get_ticker_tradevalue() # 코인 거래금액 추가
    return render_template('./admin/hotcoinsnm.html', coinlist=tickers, coindtls = coindtl, trval = trval)


@app.route('/updateset', methods=['POST'] )
def updateset():
    global rows
    uno = request.form.get('userno')
    bidsteps = request.form.get('bidsteps')
    settitle = request.form.get('settitle')
    skey = request.form.get('skey')
    g0 = request.form.get('steprate')
    g1 = request.form.get('gap01')
    g2 = request.form.get('gap02')
    g3 = request.form.get('gap03')
    g4 = request.form.get('gap04')
    g5 = request.form.get('gap05')
    g6 = request.form.get('gap06')
    g7 = request.form.get('gap07')
    g8 = request.form.get('gap08')
    g9 = request.form.get('gap09')
    r0 = request.form.get('profitrate')
    r1 = request.form.get('int01')
    r2 = request.form.get('int02')
    r3 = request.form.get('int03')
    r4 = request.form.get('int04')
    r5 = request.form.get('int05')
    r6 = request.form.get('int06')
    r7 = request.form.get('int07')
    r8 = request.form.get('int08')
    r9 = request.form.get('int09')
    hyn = request.form.get('holdon')
    dyn = request.form.get('doublechk')
    if dyn == 'on':
        dyn = 'Y'
    else:
        dyn = 'N'
    setno = request.form.get('setno')
    updatebidadmin(uno, skey, settitle, bidsteps, g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, hyn, dyn, setno)
    rows = selectsets()
    return render_template('./admin/setlistn.html', rows = rows)


@app.route('/boardlist')
def boardlist():
    items = selectboardlist(1)
    return render_template('./board/boardlist.html', items = items)


@app.route('/noticelist')
def noticelist():
    items = selectboardlist(0)
    return render_template('./board/boardlist.html', items = items)


@app.route('/boardwrite')
def boardwrite():
    return render_template('./board/boardwrite.html')


@app.route('/boardedit')
def boardedit():
    brdno = request.args.get('boardno')
    boardcont = boarddetail(brdno)
    return render_template('./board/boardedit.html', boardcont=boardcont)


@app.route('/updateboard', methods=['POST'])
def updateboard():
    brdno = request.form.get('boardno')
    brdid = request.form.get('boardid')
    btitle = request.form.get('boardtitle')
    bcontents = request.form.get('boardcontents')
    boardupdate(brdno, btitle, bcontents)
    boardcont = selectboardlist(brdid)
    return render_template('./board/boardlist.html', items = boardcont)


@app.route('/writeboard', methods=['POST'])
def writeboard():
    userid = request.form.get('userId')
    brdid = request.form.get('boardId')
    btitle = request.form.get('boardtitle')
    bcontents = request.form.get('boardcontents')
    boardnewwrite(brdid, btitle, bcontents, userid)
    return render_template('./board/boardlist.html')


@app.route('/tests')
def tests():
    return render_template('./trade/test.html')


@app.route('/help01')
def help01():
    return render_template('./help/help001.html')


@app.route('/msglist')
def msglist():
    uno = request.args.get('uno')
    items = getmessage(uno)
    print(uno)
    print(items)
    return render_template('./board/msglist.html', items = items)


@app.route('/tradestatus')
def tradestatus():
    items = tradelist()
    return render_template('./admin/tradeStat.html', items = items)


@app.route('/msgread', methods=['POST'])
def msgread():
    pla = request.get_data().decode('utf-8').split(',')
    msgno = pla[0]
    readmsg(msgno)
    return "CHECK"


@app.route('/serverStatus')
def serverStatus():
    items = servicestatus()
    return render_template('./admin/serverlist.html', items = items)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('./error/404err.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('./error/500err.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)