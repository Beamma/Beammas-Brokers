from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)

import models
@app.route('/', methods=['GET', 'POST'])
def home():
    result = models.User.query.all()
    print(result)
    return render_template("home.html", result = result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        user_name = request.form.get("user_name")
        password = models



        .check_password(request.form.get("password"))
        print(password)
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        # Retreive User And Password, Hash Password
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        user = models.User(name=user_name, email=email, ird='0', address='0', bank='0', card='0', balance='0')
        user.set_password(request.form.get("password"))
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
