from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import http.client
import json



app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)
import models



@app.route('/', methods=['GET', 'POST'])
def home():

    return render_template("home.html", status = session.get('login', None))



@app.route('/stock/<int:id>', methods=["GET", "POST"])
def stock(id):
    stock_info = models.Stock.query.filter_by(id=id).first()
    symbol = stock_info.symbol
    print(symbol)
    conn = http.client.HTTPSConnection("yahoo-finance-low-latency.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "ad2a76ef08msh111b0faa42d8165p1c3321jsn7b86be045c34",
        'x-rapidapi-host': "yahoo-finance-low-latency.p.rapidapi.com"
        }
    conn.request("GET", "/v8/finance/spark?symbols=%s&range=max&interval=15m" %symbol, headers=headers)

    res = conn.getresponse()
    data = res.read()

    stocks = data.decode("utf-8")
    dictionary = json.loads(stocks)
    stock_history = dictionary.get(symbol)
    times = stock_history.get("timestamp")
    prices = stock_history.get("close")

    stock_history = []
    for i in range(len(prices)):
        data = [str(times[i]) , prices[i]]
        stock_history.append(data)

    return render_template('stock.html', status = session.get('login', None), stock = stock_history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('login', None) != 0:
        return redirect(url_for('home', status = session.get('login', None)))
    if request.method == "POST":

        email = request.form.get("email")
        # password = models.check_password(request.form.get("password"))
        user = models.User.query.filter_by(email=email).first()
        print(check_password_hash(user.password, request.form.get("password")))
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
        return redirect(url_for('home', status = session.get('login', None)))
    if request.method == "POST":
        session['login'] = 0
        return redirect(url_for('home', status = session.get('login', None)))
    else:
        return render_template('user.html', status = session.get('login', None))



if __name__ == "__main__":
    app.run(debug=True)
