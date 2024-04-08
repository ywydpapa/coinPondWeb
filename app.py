from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import selectUsers, check_srv, setKeys , checkwallet, tradehistory, setupbid, getsetup, setonoff, checkwalletwon, getorderlist, sellmycoin, listUsers, detailuser
import pyupbit
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)
Bootstrap(app)

@app.route('/')
def home():  # put application's code here
    return render_template('./login/login.html')

@app.route('/trade', methods=['GET', 'POST'])
def trade():
    uno = request.args.get('uno')
    setkey = request.args.get('skey')
    data = getsetup(uno)
    wallet = checkwalletwon(uno,setkey)
    orderlist = getorderlist(uno)
    print(data)
    print(orderlist)
    return render_template('/trade/trademain.html', result=data, wallet=wallet, list=orderlist)

@app.route('/tradeSet', methods=['GET', 'POST'])
def tradeSet():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    return render_template('/trade/tradesetup.html', coinlist= coinlist)

@app.route('/peakcoin', methods=['GET', 'POST'])
def peakcoin():
    tickers = pyupbit.get_tickers(fiat="KRW")
    coins = []
    for ticker in tickers:
        chk = check_srv(ticker,perc = 2)
        if chk == True:
            coins.append(ticker)
        else:
            pass
        time.sleep(0.2)
    return render_template('/trade/peakcoin.html', coinlist= coins)

@app.route('/coindetail', methods=['GET', 'POST'])
def coindetail():
    uno = request.args.get('uno')
    skey = request.args.get('skey')
    orderlist = tradehistory(uno,skey)
    return render_template('/trade/coindetail.html', orderlist= orderlist)

@app.route('/tradestat', methods=['GET', 'POST'])
def tradestat():
    if request.method == "POST":
        return render_template('trade/tradestat.html')
    else:
        uno = request.args.get('uno')
        skey = request.args.get('skey')
        walletitems = checkwallet(uno, skey)
        return render_template('/trade/tradestat.html', witems = walletitems)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global uno
    global skey
    if request.method == 'GET':
        return render_template('/login/login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        row = selectUsers(uid, upw)
        if row is not None:
            try:
                session['userNo'] = row[0][0]
                session['userName'] = row[0][1]
                session['setkey'] = str(row[1])
                uno = row[0][0]
                skey = str(row[1])
                setKeys(uno, skey)
            except Exception as e:
                session['userNo'] = 0
                session['userName'] = '브라우저 재시작 필요'
                session['setkey'] = '000000'
                print(e)
            finally:
                path = '/trade?uno=' + str(uno) + '&skey=' + str(skey)
                return redirect(path)
        else:
            return '''
                <script>
                    // 경고창 
                    alert("로그인 실패, 다시 시도하세요")
                    // 이전페이지로 이동
                    history.back()
                </script>
            '''

@app.route('/setupbid', methods=['GET', 'POST'])
def setupmybid():
    if request.method == 'GET':
        pass
    else:
        uno = request.form.get('userno')
        bidsetps = request.form.get('bidsteps')
        initprice = request.form.get('initprice')
        bidrate = request.form.get('steprate')
        initprice = initprice.replace(',', '')
        askrate = request.form.get('profitrate')
        coinn = request.form.get('coinn')
        skey = request.form.get('skey')
        setupbid(uno,skey,initprice,bidsetps,bidrate,askrate,coinn)
        data = getsetup(uno)
        wallet = checkwalletwon(uno, skey)
        orderlist = getorderlist(uno)
    return redirect('/trade?uno='+uno+'&skey='+skey)


@app.route('/logout')
def logout():
    session.clear()
    return render_template('./login/login.html')


@app.route('/userAdmin')
def useradmin():
    users = listUsers()
    return render_template('./admin/useradmin.html', users=users)


@app.route('/userDetail')
def userdetail():
    userno = request.args.get('uno')
    user = detailuser(userno)
    return render_template('./admin/userDetail.html', user=user)

@app.route('/setyn', methods=['POST'])
def setyn():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    yesno = pla[1]
    setonoff(uno, yesno)
    return "YES"


@app.route('/sellcoin', methods=['POST'])
def sellcoin():
    pla = request.get_data().decode('utf-8').split(',')
    uno = pla[0]
    coinn = pla[1]
    sellmycoin(uno, coinn)
    return "YES"


if __name__ == '__main__':
    app.run( debug=True, host='0.0.0.0', port=5000)