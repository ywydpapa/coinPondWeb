from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import (selectUsers, setKeys, checkwallet, tradehistory, hotcoinlist, setupbid, getsetup, setonoff, \
                         checkwalletwon, getorderlist, sellmycoin, listUsers, detailuser, setupbidadmin, selectsets,
                         setdetail, selectsetlist, \
                         setmypasswd, updateuserdetail, updatebidadmin, settingonoff, hotcoinlist, sethotcoin,
                         selectboardlist, boarddetail, resethotcoins, \
                         boardupdate, boardnewwrite, setholdreset, getmessage, cancelorder, gettop20, tradehistorys,
                         tradelist, readmsg, gettradelog, tradedcoins, modifyLog, insertLog, getmytrlog, getmyincomes)
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
    global avprice
    uno = request.args.get('uno')
    setkey = request.args.get('skey')
    data = getsetup(uno)
    wallet = checkwalletwon(uno, setkey)
    orderlist = getorderlist(uno)
    setno = data[6]
    trset = setdetail(setno)
    print(data)
    coinn = data[0]
    crprice = pyupbit.get_current_price(coinn)
    wallets = checkwallet(uno, setkey)
    avprice = 0
    for wallett in wallets:
        if "KRW-"+wallett["currency"] == coinn:
            avprice = wallett["avg_buy_price"]
            if float(avprice) <= 0:
                avprice = 0
    if float(avprice) > 0:
        srate = round(float(crprice)/float(avprice)*100,4)
    else:
        srate = 0
    coincand = [dashcandle160(coinn)]
    listcoino = coincand[0]['open'].tolist()
    listcoinc = coincand[0]['close'].tolist()
    print(orderlist)
    return render_template('./trade/mytrademain.html', result=data, wallet=wallet, list=orderlist, trset=trset, coinopen = listcoino, coinclose = listcoinc, cprice = crprice, bsrate = srate, avprice = avprice)


@app.route('/tradeSet', methods=['GET', 'POST'])
def tradeSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    coinn = request.args.get('coinn')
    setlist = selectsetlist(9)
    print(setlist)
    return render_template('./trade/setmytrade.html', coinlist=coinlist, coinn=coinn, setlist=setlist)


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
    mysetrate = getsetup(uno)[4]
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
        mysetcoin = getsetup(uno)[0]
        for wallet in walletitems:
            if wallet['currency'] != "KRW":
                ccoin = "KRW-" + wallet['currency']
                try:
                    cpr = pyupbit.get_current_price(ccoin)
                except Exception as e:
                    cpr = 1
                curr = [wallet['currency'], cpr]
                mycoins.append(curr)
        return render_template('./trade/mywallet.html', witems=walletitems, mycoins=mycoins, mysetcoin =mysetcoin)


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
    global skey, uno
    if request.method == 'GET':
        pass
    else:
        uno = request.form.get('userno')
        bidsetps = request.form.get('bidsteps')
        initprice = request.form.get('initprice')
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
        if dyn == 'on':
            dyn = 'Y'
        else:
            dyn = 'N'
        setupbid(uno, skey, initprice, bidsetps, bidrate, askrate, coinn, svrno, tradeset, hno, dyn)
    return redirect('/trade?uno=' + uno + '&skey=' + skey)


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
        setupbidadmin(uno, skey, settitle, bidsteps, g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, hyn, dyn)
    return redirect('/setlist')


@app.route('/setlist', methods=['GET', 'POST'])
def setlist():
    global rows
    rows = selectsets()
    return render_template('./admin/setlistn.html', rows = rows)


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
    users = listUsers()
    return render_template('./trade/dashboard.html', users=users)


@app.route('/sellcoin', methods=['POST'])
def sellcoin():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    coinn = pla[1]
    sellmycoin(uno, coinn)
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('./error/404err.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('./error/500err.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)