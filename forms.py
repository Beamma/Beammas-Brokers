from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField, PasswordField, RadioField, DateField
from wtforms.widgets import PasswordInput, NumberInput
from wtforms.validators import DataRequired, Optional, ValidationError, Email
import models
from datetime import datetime

class Register(FlaskForm):

    def check_email(form, field):
        user = models.User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("Email Already Used")

    user_name = StringField("user_name", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email(), check_email])


class Login(FlaskForm):

    def existing_email(form, field):
        user = models.User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError("There Is No Account For This Email")

    password = PasswordField("password", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired(), Email(), existing_email])


class Trade(FlaskForm):

    trade = SelectField("trade", validators=[DataRequired()])
    amount = IntegerField("amount", widget=NumberInput(), validators=[DataRequired()])


class Stock(FlaskForm):

    period = SelectField("period", validators=[DataRequired()])


class All_Stock(FlaskForm):

    search = StringField("search")
    type = RadioField("type", choices=[("All", "All"), ("Company", "Company"), ("ETF", "ETF"), ("Fund", "Fund")], default="All", validators=[DataRequired()])
    category = RadioField("category", choices=[("All", "All"), ("Tech", "Tech"), ("Agriculture", "Agriculture"), ("Retail", "Retail"), ("Finance", "Finance"), ("Automotive", "Automotive")], default="All", validators=[DataRequired()])
    exchange = RadioField("exchange", choices=[("All", "All"), ("NASDAQ", "NASDAQ"), ("NYSE", "NYSE")], default="All", validators=[DataRequired()])


class Deposit(FlaskForm):

    money = IntegerField("money", widget=NumberInput(), validators=[DataRequired()])
    card = IntegerField("card", widget=NumberInput(), validators=[DataRequired()])
    cvv = IntegerField("cvv", widget=NumberInput(), validators=[DataRequired()])
