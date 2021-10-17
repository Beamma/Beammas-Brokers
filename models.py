from main import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=1000)

    stocks = db.relationship('Trade_Info', back_populates='user')
    # stocks_sell = db.relationship('Sold_Stock', back_populates='user')
    stocks_portfolio = db.relationship('Portfolio', back_populates='user')

    def __repr__(self):
        return f'<User {self.id, self.name, self.email, self.password, self.ird, self.address, self.bank, self.card, self.balance}>'

class Stock(db.Model):
    __tablename__ = 'Stock'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    logo = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    symbol = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), nullable=False)
    market = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(), nullable=False)

    users = db.relationship('Trade_Info', back_populates='stock')
    user_portfolio = db.relationship('Portfolio', back_populates='stock')
    # user_sell = db.relationship('Sold_Stock', back_populates='stock')

class Trade_Info(db.Model):
    __tablename__ = 'Trade_Info'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
    trade_date = db.Column(db.DateTime, nullable=False)
    trade_type = db.Column(db.String(), nullable=False)

    stock = db.relationship('Stock', back_populates='users')
    user = db.relationship('User', back_populates='stocks')
# db.create_all(extend_existing=True)

# class Sold_Stock(db.Model):
#     __tablename__ = 'Sold_Stock'
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     stock_id = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
#     amount = db.Column(db.Integer, nullable=False)
#     sell_price = db.Column(db.Integer, nullable=False)
#     sell_date = db.Column(db.DateTime, nullable=False)
#
#     stock = db.relationship('Stock', back_populates='user_sell')
#     user = db.relationship('User', back_populates='stocks_sell')


class Portfolio(db.Model):
    __tablename__ = 'Portfolio'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    total_purchase_price =db.Column(db.Integer, nullable=False)

    stock = db.relationship('Stock', back_populates='user_portfolio')
    user = db.relationship('User', back_populates='stocks_portfolio')
