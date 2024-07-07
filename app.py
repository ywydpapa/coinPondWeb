from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import selectUsers, check_srv, setKeys, checkwallet, tradehistory, setupbid, getsetup, setonoff, \
    checkwalletwon, getorderlist, sellmycoin, listUsers, detailuser, setupbidadmin, selectsets, setdetail, selectsetlist, setmypasswd, updateuserdetail, updatebidadmin, settingonoff, hotcoinlist, sethotcoin, selectboardlist, boarddetail, boardupdate, boardnewwrite
from comm.upbitdata import dashcandle548
import pyupbit
import os
import time
import json
import pandas as pd
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
    indexv = btccand[0].index.tolist()
    listbtc = btccand[0]['open'].tolist()
    listeth = ethcand[0]['open'].tolist()
    return render_template('./trade/dashboard.html', btccands=listbtc, ethcands=listeth, indexv=indexv, noticelist=noticelist, boarditem = boarditems)

@app.route('/trade', methods=['GET', 'POST'])
def trade():
    uno = request.args.get('uno')
    setkey = request.args.get('skey')
    data = getsetup(uno)
    wallet = checkwalletwon(uno, setkey)
    orderlist = getorderlist(uno)
    setno = data[6]
    trset = setdetail(setno)
    print(data)
    print(orderlist)
    return render_template('./trade/mytrademain.html', result=data, wallet=wallet, list=orderlist, trset=trset)


@app.route('/tradeSet', methods=['GET', 'POST'])
def tradeSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    coinn = request.args.get('coinn')
    setlist = selectsetlist(9)
    return render_template('./trade/setmytrade.html', coinlist=coinlist, coinn=coinn, setlist=setlist)


@app.route('/adminSet', methods=['GET', 'POST'])
def adminSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    coinn = request.args.get('coinn')
    return render_template('./admin/adminsetup.html', coinlist=coinlist, coinn=coinn)


@app.route('/peakcoin', methods=['GET', 'POST'])
def peakcoin():
    coins = hotcoinlist()
    return render_template('./trade/hotcoins.html', coinlist=coins)


@app.route('/coindetail', methods=['GET', 'POST'])
def coindetail():
    uno = request.args.get('uno')
    skey = request.args.get('skey')
    orderlist = tradehistory(uno, skey)
    return render_template('./trade/mytraderesult.html', orderlist=orderlist)


@app.route('/tradestat', methods=['GET', 'POST'])
def tradestat():
    if request.method == "POST":
        return render_template('trade/tradestat.html')
    else:
        uno = request.args.get('uno')
        skey = request.args.get('skey')
        walletitems = checkwallet(uno, skey)
        return render_template('./trade/mywallet.html', witems=walletitems)


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
        coinn = request.form.get('coinn')
        skey = request.form.get('skey')
        svrno = request.form.get('svrno')
        setupbid(uno, skey, initprice, bidsetps, bidrate, askrate, coinn, svrno, tradeset)
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
        setupbidadmin(uno, skey, settitle, bidsteps, g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9)
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


@app.route('/hotyn', methods=['POST'])
def hotyn():
    pla = request.get_data().decode('utf-8').split(',')
    coinn = pla[0]
    yesno = pla[1]
    print(coinn)
    print(yesno)
    sethotcoin(coinn, yesno)
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

@app.route('/hotcoins')
def hotcoins():
    tickers = pyupbit.get_tickers(fiat="KRW")
    coindtl = pyupbit.get_orderbook(ticker=tickers)
    print(coindtl)
    return render_template('./admin/hotcoinsn.html', coinlist=tickers, coindtls = coindtl)


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
    setno = request.form.get('setno')
    updatebidadmin(uno, skey, settitle, bidsteps, g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, setno)
    rows = selectsets()
    return render_template('./admin/setlistn.html', rows = rows)


@app.route('/boardlist')
def boardlist():
    items = selectboardlist(1)
    print(items)
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
    print(brdno, brdid)
    btitle = request.form.get('boardtitle')
    bcontents = request.form.get('boardcontents')
    print(brdno, brdid, btitle, bcontents)
    boardupdate(brdno, btitle, bcontents)
    boardcont = selectboardlist(brdid)
    print(boardcont)
    return render_template('./board/boardlist.html', boardcont=boardcont)


@app.route('/writeboard', methods=['POST'])
def writeboard():
    userid = request.form.get('userId')
    brdid = request.form.get('boardId')
    btitle = request.form.get('boardtitle')
    bcontents = request.form.get('boardcontents')
    print(brdid, btitle, bcontents)
    boardnewwrite(brdid, btitle, bcontents, userid)
    return render_template('./board/boardlist.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
