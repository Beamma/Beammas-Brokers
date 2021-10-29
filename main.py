from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy import insert
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import http.client
import json
import yfinance as yf
import datetime
import os


cache = Cache()

app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config["SESSION_TYPE"] = "memcached"
app.config["SECRET_KEY"] = "super secret key"
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "sup3r_secr3t_passw3rd"
db = SQLAlchemy(app)
app.config["CACHE_TYPE"] = "simple"
cache.init_app(app)
import models
from forms import Register, Login, Trade, Stock, All_Stock, Deposit

def history_price(symbol, period, interval):
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=period, interval=interval)
    return(history)

# @cache.cached(timeout=600)


def info_stock(symbol):
    ticker = yf.Ticker(symbol)
    ticker_info = ticker.info
    return(ticker_info)


@app.route("/")
def home():
    if session.get(
        "login",
            None) is None:  # If first time on site, set neccesary sessions
        session["login"] = 0
        session["admin"] = 0
        session["update"] = None
    return render_template(
        "home.html",
        status=session.get(
            "login",
            None),
        admin=session.get("admin"))


@app.route("/stock", methods=["GET", "POST"])
def all_stock():
    form = All_Stock()
    # Check If user is logged in, if not redirect for login
    if session.get("login", None) == 0:
        return redirect(
            url_for(
                "login",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    if request.method == "POST":
        # Search for stock
        search = form.search.data
        if search:
            stock_info = models.Stock.query.filter_by(symbol=search).all()
        else:

            # Stock Filters
            type = form.type.data
            category = form.category.data
            market = form.exchange.data
            if type != "All" and category != "All" and market != "All":
                stock_info = models.Stock.query.filter_by(
                    type=type, category=category, market=market).all()

            if type != "All" and category != "All" and market == "All":
                stock_info = models.Stock.query.filter_by(
                    type=type, category=category).all()

            if type != "All" and category == "All" and market != "All":
                stock_info = models.Stock.query.filter_by(
                    type=type, market=market).all()

            if type == "All" and category != "All" and market != "All":
                stock_info = models.Stock.query.filter_by(
                    category=category, market=market).all()

            if type != "All" and category == "All" and market == "All":
                stock_info = models.Stock.query.filter_by(type=type).all()

            if type == "All" and category != "All" and market == "All":
                stock_info = models.Stock.query.filter_by(
                    category=category).all()

            if type == "All" and category == "All" and market != "All":
                stock_info = models.Stock.query.filter_by(market=market).all()

            if type == "All" and category == "All" and market == "All":
                stock_info = models.Stock.query.all()

        return render_template(
            "all_stock.html",
            status=session.get(
                "login",
                None),
            stock_info=stock_info,
            admin=session.get("admin"),
            form=form)
    else:
        stock_info = models.Stock.query.all()
    return render_template(
        "all_stock.html",
        status=session.get(
            "login",
            None),
        stock_info=stock_info,
        admin=session.get("admin"),
        form=form)


@app.route("/stock/<symbol>", methods=["GET", "POST"])
# @cache.cached(timeout=120)
def stock(symbol):
    form = Stock()
    form.period.choices = [
        ("max",
         "Max"),
        ("5y",
         "5 Years"),
        ("2y",
         "2 Years"),
        ("1y",
         "1 Year"),
        ("6mo",
         "6 Months"),
        ("1mo",
         "1 Month"),
        ("14d",
         "2 Weeks"),
        ("7d",
         "1 Week"),
        ("2d",
         "2 Days"),
        ("1d",
         "1 Day"),
        ("1h",
         "1 Hour")]
    maximum = 0
    # Check If user is logged in, if not redirect for login
    if session.get("login", None) == 0:
        return redirect(
            url_for(
                "login",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    if request.method == "POST":
        # Select interval for API/Graph based off the period selected
        period = form.period.data
        periods = {
            "max": "1d",
            "5y": "1d",
            "2y": "1d",
            "1y": "1d",
            "6mo": "1d",
            "1mo": "1h",
            "14d": "1h",
            "7d": "30m",
            "2d": "5m",
            "1d": "5m",
            "1h": "1m"}
        interval = periods[period]
    else:
        # Default Values
        period = "7d"
        interval = "30m"

    # Get stock price history
    stock_info = models.Stock.query.filter_by(symbol=symbol).first()
    if stock_info is None:
        return redirect(url_for("all_stock"))
    symbol = stock_info.symbol
    history = history_price(symbol, period, interval)
    # Add date and price in feasable format for graph
    stock_history = []
    for index in history.index:
        date_price = [index, history.loc[index]["Close"]]
        stock_history.append(date_price)

    # Cacluclate info for given periods
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="1h", interval="1h")
    current_price = []
    for index in history.index:
        date_price = [index, history.loc[index]["Close"]]
        current_price.append(date_price)
    current = format(current_price[-1][1], ".2f")

    ticker_info = info_stock(symbol)
    maximum = format(max(history["High"]), ".2f")
    low = format(min(history["Low"]), ".2f")
    price_change = format(
        (stock_history[-1][1] - stock_history[0][1]) / stock_history[0][1] * 100, ".2f")
    open = format(stock_history[0][1], ".2f")
    market_cap = ticker_info["marketCap"]
    yields = ticker_info["fiveYearAvgDividendYield"]
    price_info = {
        "Max": maximum,
        "Low": low,
        "Current": current,
        "Price Change": price_change,
        "Open": open,
        "Market Cap": market_cap,
        "Five Year Dividend Yield": yields}

    return render_template(
        "stock.html",
        status=session.get(
            "login",
            None),
        admin=session.get("admin"),
        stock=stock_history,
        stock_info=stock_info,
        period=period,
        price_info=price_info,
        form=form)


@app.route("/stock/trade/<symbol>", methods=["GET", "POST"])
# @cache.cached(timeout=120)
def trade(symbol):
    form = Trade()
    form.trade.choices = [("Buy", "Buy"), ("Sell", "Sell")]
    stock_info = models.Stock.query.filter_by(symbol=symbol).first()
    if stock_info is None:
        return redirect(url_for("all_stock"))
    # Check If user is logged in, if not redirect for login
    if session.get("login", None) == 0:
        return redirect(
            url_for(
                "login",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    else:
        # Get essential info
        user_info = models.User.query.filter_by(
            id=session.get("login", None)).first()
        user_balance = user_info.balance

        # Get Latest Price
        ticker_info = info_stock(symbol)
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1h", interval="1h")
        current_price = []
        for index in history.index:
            date_price = [index, history.loc[index]["Close"]]
            current_price.append(date_price)
        stock_price = current_price[-1][1]

        # Get portfolio of user
        portfolio = models.Portfolio.query.filter_by(
            user_id=session.get("login", None), stock_id=stock_info.id).first()

        # check if user owns any stock if not set to 0
        if portfolio is None:
            stocks_owned = 0
        else:
            stocks_owned = portfolio.amount

        # Get Stock Reciepts
        recent_purchases = models.Trade_Info.query.filter_by(
            user_id=session.get(
                "login", None), stock_id=stock_info.id).order_by(
            models.Trade_Info.id.desc()).all()

        if request.method == "POST":
            stock = models.Stock.query.filter_by(symbol=symbol).all()

            if form.validate_on_submit():
                trade = form.trade.data
                amount = form.amount.data
            else:
                return render_template(
                    "trade.html",
                    status=session.get(
                        "login",
                        None),
                    admin=session.get("admin"),
                    stocks_owned=stocks_owned,
                    stock_info=stock_info,
                    stock_price=format(
                        stock_price,
                        ".2f"),
                    user_balance=format(
                        user_balance,
                        ".2f"),
                    recent_purchases=recent_purchases,
                    form=form)
            # Buy
            if trade == "Buy":
                # Check to make sure user has enough money to buy
                if user_balance >= amount * int(stock_price):
                    trade = models.Trade_Info(
                        stock_id=stock[0].id,
                        user_id=session.get(
                            "login",
                            None),
                        amount=request.form.get("amount"),
                        trade_price=stock_price,
                        trade_date=datetime.datetime.now(),
                        trade_type="Buy")
                    db.session.add(trade)
                    existing_stock = models.Portfolio.query.filter_by(
                        user_id=session.get("login", None), stock_id=stock[0].id).first()
                    purchase_price = int(
                        request.form.get("amount")) * stock_price

                    # Update Portfolio DB Amount If Required
                    if existing_stock:
                        new_amount = int(existing_stock.amount) + \
                            int(request.form.get("amount"))
                        new_total_purchase_price = purchase_price + existing_stock.total_purchase_price
                        existing_stock.amount = new_amount
                        existing_stock.total_purchase_price = new_total_purchase_price
                        db.session.merge(existing_stock)

                    else:
                        portfolio = models.Portfolio(
                            stock_id=stock[0].id,
                            user_id=session.get(
                                "login",
                                None),
                            amount=request.form.get("amount"),
                            total_purchase_price=purchase_price)
                        db.session.add(portfolio)

                    # Update User Balance (Subtract Price * Amount)
                    user_balance = format(user_balance - purchase_price, ".2f")
                    user_info.balance = user_balance
                    db.session.merge(user_info)
                    db.session.commit()

                else:
                    error_status = "Failed. You Currently Cannot Afford"  # set error status
                    return render_template(
                        "trade.html",
                        status=session.get(
                            "login",
                            None),
                        admin=session.get("admin"),
                        stocks_owned=stocks_owned,
                        stock_info=stock_info,
                        stock_price=format(
                            stock_price,
                            ".2f"),
                        user_balance=user_balance,
                        recent_purchases=recent_purchases,
                        error_status=error_status,
                        form=form)

            # Sell
            if trade == "Sell":
                # Get amount of stock user want to sell, and amount of stock
                # user has
                amount = int(request.form.get("amount"))
                portfolio = models.Portfolio.query.filter_by(
                    user_id=session.get("login", None), stock_id=stock[0].id).first()

                # If stock amount selling is = to owned, delete completely
                if portfolio.amount == amount:
                    db.session.delete(db.session.merge(portfolio))
                    user_info.balance = user_balance + \
                        (int(amount) * int(stock_price))
                    db.session.merge(user_info)

                    trade = models.Trade_Info(
                        stock_id=stock[0].id,
                        user_id=session.get(
                            "login",
                            None),
                        amount=request.form.get("amount"),
                        trade_price=stock_price,
                        trade_date=datetime.datetime.now(),
                        trade_type="Sell")
                    db.session.add(trade)

                    db.session.commit()

                # If stock amount owned is greater than selling, update leaving
                # remaining stock in users portfolio
                if portfolio.amount > amount:
                    portfolio.amount = int(portfolio.amount) - int(amount)
                    portfolio.total_purchase_price = portfolio.total_purchase_price - \
                        (int(amount) * int(stock_price))
                    db.session.merge(portfolio)
                    user_info.balance = user_balance + \
                        (int(amount) * int(stock_price))
                    db.session.merge(user_info)

                    trade = models.Trade_Info(
                        stock_id=stock[0].id,
                        user_id=session.get(
                            "login",
                            None),
                        amount=request.form.get("amount"),
                        trade_price=stock_price,
                        trade_date=datetime.datetime.now(),
                        trade_type="Sell")
                    db.session.add(trade)

                    db.session.commit()

                # Otherwise dont allow any sell and send error message
                else:
                    error_status = "Failed. You Do Not Own Enough Stock."
                    return render_template(
                        "trade.html",
                        status=session.get(
                            "login",
                            None),
                        admin=session.get("admin"),
                        stocks_owned=stocks_owned,
                        stock_info=stock_info,
                        stock_price=format(
                            stock_price,
                            ".2f"),
                        user_balance=format(
                            user_balance,
                            ".2f"),
                        recent_purchases=recent_purchases,
                        error_status=error_status,
                        form=form)
            return redirect(request.url)

        return render_template(
            "trade.html",
            status=session.get(
                "login",
                None),
            admin=session.get("admin"),
            stocks_owned=stocks_owned,
            stock_info=stock_info,
            stock_price=format(
                stock_price,
                ".2f"),
            user_balance=format(
                user_balance,
                ".2f"),
            recent_purchases=recent_purchases,
            form=form)


@app.route("/admin", methods=["GET", "POST"])
def admin():

    # check if suer is admin if not redirect to home
    if session.get("admin") != 1:
        return redirect(
            url_for(
                "home",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    else:
        delete_status = ""
        update_status = ""  # Set update status to false (no error status)
        submitted = None  # Set submitted status to false (no error status)

        if request.method == "POST":

            # Check Radio Selection, From then run neccesary updates/ deletes
            radio = request.form.get("create_delete")
            if radio == "create":
                # Create
                img_file = request.files["logo"]
                symbol = request.form.get("ticker")
                ticker = yf.Ticker(symbol)
                ticker_info = ticker.info
                # Check to see if inputs valid
                valid = [
                    img_file,
                    ticker_info,
                    request.form.get("type"),
                    request.form.get("market"),
                    request.form.get("category")]
                if "" in valid:
                    submitted = False
                    return render_template(
                        "admin.html",
                        status=session.get(
                            "login",
                            None),
                        admin=session.get("admin"),
                        delete_status=delete_status,
                        submitted=submitted,
                        update_status=update_status)
                img_file.save(os.path.join("static/", img_file.filename))
                img_location = img_file.filename

                stock = models.Stock(
                    name=ticker_info["shortName"],
                    logo=img_location,
                    description=ticker_info["longBusinessSummary"],
                    symbol=symbol,
                    type=request.form.get("type"),
                    market=request.form.get("market"),
                    category=request.form.get("category"))
                db.session.add(stock)
                db.session.commit()
                submitted = True
            if radio == "delete":
                # Delete
                delete_stock = request.form.get("delete")
                delete = models.Stock.query.filter_by(
                    symbol=delete_stock).first()
                if delete is None:
                    delete_status = "Invalid Stock Ticker"
                else:
                    db.session.delete(db.session.merge(delete))
                    db.session.commit()
                    delete_status = "Deleted Stock"
            if radio == "update":
                # Update
                update = request.form.get("update")
                session["update"] = update
                # Check to make sure stock selected is real, if is redirect for
                # url
                stock = models.Stock.query.filter_by(symbol=update).first()
                if stock is not None:
                    return redirect(url_for("update"))
                else:
                    update_status = "Failed Stock Doesnt Exist"  # pass error status
        return render_template(
            "admin.html",
            status=session.get(
                "login",
                None),
            admin=session.get("admin"),
            delete_status=delete_status,
            submitted=submitted,
            update_status=update_status)


@app.route("/admin/update", methods=["GET", "POST"])
def update():
    update = session.get("update")  # call stock to update

    # check to make sure user is admin and has submitted a stock to update
    if session.get("admin") == 1 and update is not None:
        stock = models.Stock.query.filter_by(symbol=update).first()
        if request.method == "POST":
            # Check if new img been uploaded if so, update if not pass
            if not request.files.get("file", None):
                pass
            else:
                img_file = request.files["logo"]
                img_file.save(os.path.join("static/", img_file.filename))
                stock.logo = img_file.filename

            stock.name = request.form.get("name")
            stock.description = request.form.get("description")
            stock.symbol = request.form.get("ticker")
            stock.type = request.form.get("type")
            stock.market = request.form.get("market")
            stock.category = request.form.get("category")
            db.session.merge(stock)
            db.session.commit()

        return render_template(
            "update.html",
            status=session.get(
                "login",
                None),
            admin=session.get("admin"),
            stock=stock)
    else:
        return redirect(
            url_for(
                "home",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    # Make sure user isnt already logged in
    if session.get("login", None) != 0:
        return redirect(
            url_for(
                "home",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    if request.method == "POST":
        # Get forms and check if valid
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
        else:
            return render_template(
                "login.html",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin"),
                form=form)

        # Check if users password is correct
        user = models.User.query.filter_by(email=email).first()
        if check_password_hash(user.password, password) is True:
            # Set users session, (making them logged in)
            session["login"] = user.id
            session["admin"] = user.admin
            return redirect(
                url_for(
                    "home",
                    status=session.get(
                        "login",
                        None),
                    admin=session.get("admin")))

        else:
            # Otherwise makesure the user is set as logged out
            session["login"] = 0
            error_status = "Wrong Password"
            return render_template(
                "login.html",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin"),
                error=error_status,
                form=form)
    else:
        return render_template(
            "login.html",
            status=session.get(
                "login",
                None),
            admin=session.get("admin"),
            form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = Register()
    if session.get("login", None) != 0:
        return redirect(
            url_for(
                "home",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))
    if request.method == "POST":

        # Retreive form
        if form.validate_on_submit():
            name = form.user_name.data
            email = form.email.data
            password = form.password.data
            # Add user to data base
            user = models.User(
                name=name,
                password=generate_password_hash(password),
                email=email,
                admin=0,
                balance="1000")
            db.session.add(user)
            db.session.commit()

            # Log user in using id
            user = models.User.query.filter_by(email=email).first()
            session["login"] = user.id
            return redirect(
                url_for(
                    "home",
                    status=session.get(
                        "login",
                        None),
                    admin=session.get("admin"),
                    form=form))
        # If form not valid return errors
        else:
            return render_template(
                "register.html",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin"),
                form=form)
    else:
        return render_template(
            "register.html",
            status=session.get(
                "login",
                None),
            admin=session.get("admin"),
            form=form)


@app.route("/user", methods=["GET", "POST"])
# @cache.cached(timeout=60)
def user():

    # Log user out
    if request.method == "POST":
        session["login"] = 0
        return redirect(
            url_for(
                "home",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    # Check if user is logged in
    if session.get("login", None) == 0:
        return redirect(
            url_for(
                "login",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    else:
        # Get user info and there portfolio
        User = models.User.query.filter_by(
            id=session.get("login", None)).first()
        user_balance = format(User.balance, ".2f")
        Portfolio = models.Portfolio.query.filter_by(
            user_id=session.get("login", None)).all()
        print(Portfolio)
        if Portfolio == []:
            return render_template(
                "user.html",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin"),
                User=User,
                user_balance=user_balance,
                portfolio_value="0",
                portfolio_purchase_price="0",
                net_profit="0",
                total_ROI="0",
                no_reciepts=True)
        # Calculate portfolio value and purchase price
        stocks = []
        portfolio_value = 0
        portfolio_purchase_price = 0
        for i in range(len(Portfolio)):
            stock_info = []
            stock_info.append(Portfolio[i].stock.name)
            stock_info.append(Portfolio[i].amount)
            # Get Current Stock Price
            stock = models.Stock.query.filter_by(
                id=Portfolio[i].stock_id).first()
            ticker = yf.Ticker(stock.symbol)
            history = ticker.history(period="1h", interval="1h")
            stock_history = []
            for index in history.index:
                date_price = [index, history.loc[index]["Close"]]
                stock_history.append(date_price)
            stock_price = stock_history[-1][1]

            # Calculate Actual ROI (Return On Investment) For Each Stock
            total_investment = format(Portfolio[i].total_purchase_price, ".2f")
            total_worth = format(Portfolio[i].amount * stock_price, ".2f")
            total_profit = format(
                (Portfolio[i].amount *
                 stock_price) -
                Portfolio[i].total_purchase_price,
                ".2f")
            ROI = format(
                (((Portfolio[i].amount *
                   stock_price) -
                  Portfolio[i].total_purchase_price) /
                    Portfolio[i].total_purchase_price) *
                100,
                ".2f")
            stock_info.extend(
                [format(stock_price, ".2f"), total_investment, total_worth, total_profit, ROI])

            stock_info.append(stock.symbol)
            stocks.append(stock_info)
            portfolio_purchase_price = portfolio_purchase_price + \
                Portfolio[i].total_purchase_price
            portfolio_value = portfolio_value + \
                (Portfolio[i].amount * stock_price)

        # Calculate Total ROI and net profit
        net_profit = portfolio_value - portfolio_purchase_price
        total_ROI = 100 * net_profit / portfolio_purchase_price

        # Display User reciepts
        recent_purchases = models.Trade_Info.query.filter_by(
            user_id=session.get(
                "login", None)).order_by(
            models.Trade_Info.id.desc()).all()
        return render_template(
            "user.html", status=session.get(
                "login", None), admin=session.get("admin"), User=User, stocks=stocks, portfolio_value=format(
                portfolio_value, ".2f"), portfolio_purchase_price=format(
                portfolio_purchase_price, ".2f"), net_profit=format(
                    net_profit, ".2f"), total_ROI=format(
                        total_ROI, ".2f"), recent_purchases=recent_purchases, user_balance=user_balance)


@app.route("/user/deposit", methods=["GET", "POST"])
def deposit():
    form = Deposit()
    user = models.User.query.filter_by(id=session.get("login", None)).first()
    work_status = ""
    # Check If user is logged in, if not redirect for login
    if session.get("login", None) == 0:
        return redirect(
            url_for(
                "login",
                status=session.get(
                    "login",
                    None),
                admin=session.get("admin")))

    else:
        if request.method == "POST":

            if form.validate_on_submit():
                work_status = "Failed Please Try Again"
            else:
                work_status = "Funds Deposited"
            money = form.money.data

            # update balance
            user.balance = money + user.balance
            db.session.merge(user)
            db.session.commit()

    return render_template(
        "deposit.html",
        status=session.get(
            "login",
            None),
        admin=session.get("admin"),
        form=form,
        user=user,
        work_status=work_status)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=(str(e)))


if __name__ == "__main__":
    app.run(debug=True)
