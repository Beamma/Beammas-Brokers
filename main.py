from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # applying all config to app
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
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
