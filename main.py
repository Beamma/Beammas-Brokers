from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import http.client
import json
import yfinance as yf
import datetime


app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)
import models



@app.route('/')
def home():
    if session.get('login', None) == None:
        session['login'] = 0
    return render_template("home.html")


@app.route('/stock', methods=['GET', 'POST'])
def all_stock():
    if session.get('login', None) == None:
        session['login'] = 0
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))

    stock_info = models.Stock.query.all()
    return render_template("all_stock.html", status = session.get('login', None), stock_info=stock_info)






@app.route('/stock/<symbol>', methods=["GET", "POST"])
def stock(symbol):
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))
    if request.method == "POST":
        periods = {'max': '1d', '5y': '1d', '2y': '1d', '1y': '1d', '6mo': '1d', '1mo': '1h', '14d': '1h', '7d': '30m', '2d': '5m', '1d': '5m', '1h': '1m'}
        period = request.form.get("period")
        interval = periods[period]
    else:
        period = '7d'
        interval = '30m'
    stock_info = models.Stock.query.filter_by(symbol=symbol).first()
    symbol = stock_info.symbol
    print(symbol)
    ticker = yf.Ticker(symbol)
    print(ticker)
    history = ticker.history(period=period, interval=interval)
    stock_history = []
    for index in history.index:
        date_price = [index, history.loc[index]['Close']]
        stock_history.append(date_price)
    return render_template('stock.html', status = session.get('login', None), stock = stock_history, stock_info = stock_info)




@app.route('/stock/trade/<symbol>', methods=["GET", "POST"])
def trade(symbol):
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))
    else:
        user_info = models.User.query.filter_by(id=session.get('login', None)).first()
        user_balance = user_info.balance
        stock_info = models.Stock.query.filter_by(symbol=symbol).first()

        # Get Latest Price (Imporvement Needed)
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1h", interval="1h")
        stock_history = []
        for index in history.index:
            date_price = [index, history.loc[index]['Close']]
            stock_history.append(date_price)
        stock_price = stock_history[-1][1]

        portfolio = models.Portfolio.query.filter_by(user_id=session.get('login', None), stock_id=stock_info.id).first()
        stocks_owned = portfolio.amount

        recent_purchases = models.Trade_Info.query.filter_by(user_id=session.get('login', None), stock_id=stock_info.id).order_by(models.Trade_Info.id.desc()).all()
        # print(recent_purchases.order_by(recent_purchases.id.desc()))

        if request.method == "POST":
            stock = models.Stock.query.filter_by(symbol=symbol).all()
            if request.form.get("trade") == "buy":
                if user_balance >= int(request.form.get("amount")) * int(stock_price):
                    trade = models.Trade_Info(stock_id=stock[0].id, user_id=session.get('login', None), amount=request.form.get("amount"), trade_price=stock_price, trade_date=datetime.datetime.now(), trade_type="Buy")

                    db.session.add(trade)
                    existing_stock = models.Portfolio.query.filter_by(user_id=session.get('login', None), stock_id=stock[0].id).first()
                    purchase_price = int(request.form.get("amount")) * stock_price
                    # Update Portfolio DB Amount If Required
                    if existing_stock:
                        new_amount = int(existing_stock.amount) + int(request.form.get("amount"))
                        new_total_purchase_price = purchase_price + existing_stock.total_purchase_price
                        existing_stock.amount = new_amount
                        existing_stock.total_purchase_price = new_total_purchase_price
                        db.session.merge(existing_stock)
                    else:
                        print("none")
                        portfolio = models.Portfolio(stock_id=stock[0].id, user_id=session.get('login', None), amount=request.form.get("amount"), total_purchase_price=purchase_price)
                        db.session.add(portfolio)

                    # Update User Balance (Subtract Price * Amount)
                    user_balance = user_balance - purchase_price
                    user_info.balance = user_balance
                    db.session.merge(user_info)
                    db.session.commit()
                else:
                    print("Failed")


            if request.form.get("trade") == "sell":
                print("sell")
                amount = int(request.form.get("amount"))
                portfolio = models.Portfolio.query.filter_by(user_id=session.get('login', None), stock_id=stock[0].id).first()
                print(portfolio)
                if portfolio.amount == amount:
                    print("Sell All")
                    db.session.delete(db.session.merge(portfolio))
                    user_info.balance = user_balance + (int(amount) * int(stock_price))
                    db.session.merge(user_info)

                    trade = models.Trade_Info(stock_id=stock[0].id, user_id=session.get('login', None), amount=request.form.get("amount"), trade_price=stock_price, trade_date=datetime.datetime.now(), trade_type="Sell")
                    db.session.add(trade)

                    db.session.commit()
                if portfolio.amount >  amount:
                    portfolio.amount = int(portfolio.amount) - int(amount)
                    portfolio.total_purchase_price = portfolio.total_purchase_price - (int(amount) * int(stock_price))
                    db.session.merge(portfolio)
                    user_info.balance = user_balance + (int(amount) * int(stock_price))
                    db.session.merge(user_info)

                    trade = models.Trade_Info(stock_id=stock[0].id, user_id=session.get('login', None), amount=request.form.get("amount"), trade_price=stock_price, trade_date=datetime.datetime.now(), trade_type="Sell")
                    db.session.add(trade)

                    db.session.commit()
                else:
                    print("No")
            return redirect(request.url)

        return render_template('trade.html', status = session.get('login', None), stocks_owned=stocks_owned, stock_info=stock_info, stock_price = stock_price, user_balance=user_balance, recent_purchases=recent_purchases)





@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('login', None) != 0:
        return redirect(url_for('home', status = session.get('login', None)))
    if request.method == "POST":

        email = request.form.get("email")
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
    if request.method == "POST":
        session['login'] = 0
        return redirect(url_for('home', status = session.get('login', None)))
    if session.get('login', None) == 0:
        return redirect(url_for('login', status = session.get('login', None)))
    else:
        User = models.User.query.filter_by(id=session.get('login', None)).first()
        Portfolio = models.Portfolio.query.filter_by(user_id=session.get('login', None)).all()
        stocks = []
        portfolio_value = 0
        portfolio_purchase_price = 0
        for i in range(len(Portfolio)):
            stock_info = []
            stock_info.append(Portfolio[i].stock.name)
            stock_info.append(Portfolio[i].amount)

            # Calculate Percentage Increase

            # Get Current Stock Price
            stock = models.Stock.query.filter_by(id=Portfolio[i].stock_id).first()
            ticker = yf.Ticker(stock.symbol)
            history = ticker.history(period="1h", interval="1h")
            stock_history = []
            for index in history.index:
                date_price = [index, history.loc[index]['Close']]
                stock_history.append(date_price)
            stock_price = stock_history[-1][1]

            # Calculate Actual ROI (Return On Investment) For Each Stock
            ROI = format((((Portfolio[i].amount * stock_price) - Portfolio[i].total_purchase_price)/Portfolio[i].total_purchase_price) * 100, '.2f')
            stock_info.append(ROI)
            stock_info.append(stock.symbol)
            stocks.append(stock_info)
            portfolio_purchase_price = portfolio_purchase_price + Portfolio[i].total_purchase_price
            portfolio_value = portfolio_value + (Portfolio[i].amount * stock_price)
        net_profit = portfolio_value - portfolio_purchase_price
        total_ROI = 100 * net_profit / portfolio_purchase_price

        recent_purchases = models.Trade_Info.query.filter_by(user_id=session.get('login', None)).order_by(models.Trade_Info.id.desc()).all()

        return render_template('user.html', status = session.get('login', None), User=User, stocks=stocks, portfolio_value=format(portfolio_value, '.2f'), portfolio_purchase_price=format(portfolio_purchase_price, '.2f'), net_profit=format(net_profit, '.2f'), total_ROI=format(total_ROI, '.2f'), recent_purchases=recent_purchases)






if __name__ == "__main__":
    app.run(debug=True)
