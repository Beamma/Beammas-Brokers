from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import http.client
import json
import yfinance as yf


app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)
import models





@app.route('/', methods=['GET', 'POST'])
def home():
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))

    stock_info = models.Stock.query.all()
    return render_template("home.html", status = session.get('login', None), stock_info=stock_info)






@app.route('/stock/<symbol>', methods=["GET", "POST"])
def stock(symbol):
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))
    if request.method == "POST":
        periods = {'max': '1d', '5y': '1d', '2y': '1d', '1y': '1d', '6mo': '1d', '1mo': '1h', '14d': '1h', '7d': '30m', '2d': '5m', '1d': '5m', '1h': '1m'}
        period = request.form.get("period")
        interval = periods[period]
    else:
        period = 'max'
        interval = '1d'
    stock_info = models.Stock.query.filter_by(symbol=symbol).first()
    symbol = stock_info.symbol
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=period, interval=interval)
    stock_history = []
    for index in history.index:
        date_price = [index, history.loc[index]['Close']]
        stock_history.append(date_price)
    return render_template('stock.html', status = session.get('login', None), stock = stock_history, stock_info = stock_info)





@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('login', None) != 0:
        return redirect(url_for('home', status = session.get('login', None)))
    if request.method == "POST":

        email = request.form.get("email")
        # password = models.check_password(request.form.get("password"))
        user = models.User.query.filter_by(email=email).first()
        if user is None:
            return redirect(url_for('login', status = session.get('login', None)))
        if check_password_hash(user.password, request.form.get("password")) is True:
            session['login'] = user.id
            return redirect(url_for('home', status = session.get('login', None)))
        else:
            session['login'] = 0
            return redirect(url_for('login', status = session.get('login', None)))
    else:
        return render_template("login.html", status = session.get('login', None))






@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('login', None) != 0:
        return redirect(url_for('home', status = session.get('login', None)))
    if request.method == "POST":

        # Retreive User And Password, Hash Password
        email = request.form.get("email")
        user = models.User.query.all()
        for user in user:
            print(email, user.email)
            if email == user.email:
                print("Match")
                return redirect(url_for('register', status = session.get('login', None)))


        user = models.User(name=request.form.get("user_name"), password=generate_password_hash(request.form.get("password")), email=email, ird='0', address='0', bank='0', card='0', balance='0')
        db.session.add(user)
        db.session.commit()

        user = models.User.query.filter_by(email=email).first()
        session['login'] = user.id
        return redirect(url_for('home', status = session.get('login', None)))
    else:
        return render_template("register.html", status = session.get('login', None))






@app.route('/user', methods=['GET', 'POST'])
def user():
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))
    if request.method == "POST":
        session['login'] = 0
        return redirect(url_for('home', status = session.get('login', None)))
    else:
        return render_template('user.html', status = session.get('login', None))






if __name__ == "__main__":
    app.run(debug=True)
