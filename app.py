from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import selectUsers, check_srv, setKeys , checkwallet, tradehistory, setupbid, getsetup, setonoff, checkwalletwon
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
    if request.method == 'GET':
        uno = request.args.get('uno')
        setkey = request.args.get('skey')
        data = getsetup(uno)
        wallet = checkwalletwon(uno,setkey)
        print(data)
        return render_template('/trade/trademain.html', result=data, wallet=wallet)
    else:
        return render_template('/trade/trademain.html')

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
    if request.method == 'GET':
        return render_template('/login/login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        row = selectUsers(uid, upw)
        if row:
            if row[0][0] is not None:
                session['userNo'] = row[0][0]
            else:
                pass
            if row[0][1] is not None:
                session['userName'] = row[0][1]
            else:
                pass
            if row[1] is not None:
                session['setkey'] = str(row[1])
            else:
                pass
            uno = row[0][0]
            ukey = str(row[1])
            setKeys(uno, ukey)
            path = '/trade?uno=' + str(uno) + '&skey=' + str(ukey)
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
    return render_template('/trade/trademain.html', result=data)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('./login/login.html')

@app.route('/setyn', methods=['POST'])
def setyn():
    pla = list(request.get_data().decode('utf-8'))
    uno = pla[0]
    yesno = pla[2]
    setonoff(uno, yesno)
    return "YES"


if __name__ == '__main__':
    app.run( debug=True, host='0.0.0.0', port=5000)