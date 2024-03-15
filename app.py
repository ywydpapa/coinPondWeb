from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from comm.dbconn import selectUsers, check_srv
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
    coinlist = pyupbit.get_tickers(fiat="KRW")
    return render_template('/trade/trademain.html', coinlist= coinlist)

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
    coinlist = pyupbit.get_tickers(fiat="KRW")
    return render_template('/trade/coindetail.html', coinlist= coinlist)

@app.route('/tradestat', methods=['GET', 'POST'])
def tradestat():
    coinlist = pyupbit.get_tickers(fiat="KRW")
    return render_template('/trade/tradestat.html', coinlist= coinlist)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/login/login.html')
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        row = selectUsers(uid, upw)
        if row:
            session['userName'] = row[1]
            return redirect('/trade')
        else:
            return '''
                <script>
                    // 경고창 
                    alert("로그인 실패, 다시 시도하세요")
                    // 이전페이지로 이동
                    history.back()
                </script>
            '''

@app.route('/logout')
def logout():
    session.clear()
    return render_template('./login/login.html')

if __name__ == '__main__':
    app.run()