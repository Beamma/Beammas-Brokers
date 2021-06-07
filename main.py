from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)

import models
@app.route('/', methods=['GET', 'POST'])
def home():
    result = models.User.query.filter_by(id=1).all()
    print(result)
    return render_template("home.html", result = result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        # Retreive User And Password, Hash Password
        user_name = request.form.get("user_name")
        hashed_password = generate_password_hash(request.form.get("password"), salt_length=10)
        email = request.form.get("email")
        print(user_name, hashed_password, email) # DEBUG
        user.insert().values(name=user_name, email=email, pass_word=hashed_password, ird=0, bank=0, card=0, adress=0, balance=0)

        return redirect(url_for('home'))
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
