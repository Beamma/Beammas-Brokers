from flask_wtf import FlaskForm
from wtforms import IntegerField, TextField, TextAreaField, SelectField, StringField, PasswordField
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, Optional, ValidationError, Email
import models
from datetime import datetime

class Register(FlaskForm):

    def check_email(form, field):
        user = models.User.query.filter_by(email=field.data).first()
        if user != None:
            raise ValidationError("Email Already Used")

    user_name = TextField("user_name", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email(), check_email])

class Login(FlaskForm):

    def exisiting_email(form, field):
        user = models.User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError("There Is No Account For This Email")

    password = PasswordField("password", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email(), exisiting_email])

class Trade(FlaskForm):

    trade = SelectField("trade", validators=[DataRequired()])
    amount = IntegerField("amount", validators=[DataRequired()])
