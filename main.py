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
    result = models.User.query.all()
    # print(result)
    return render_template("home.html", result = result)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        # password = models.check_password(request.form.get("password"))
        password = models.User.query.filter_by(email=email).first()
        print(check_password_hash(password.password, request.form.get("password")))
        return render_template("login.html")
    else:
        return render_template("login.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        # Retreive User And Password, Hash Password
        user = models.User(name=request.form.get("user_name"), password=generate_password_hash(request.form.get("password")), email=request.form.get("email"), ird='0', address='0', bank='0', card='0', balance='0')
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template("register.html")



if __name__ == "__main__":
    app.run(debug=True)
