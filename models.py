from main import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    ird = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(), nullable=False)
    bank = db.Column(db.Integer, nullable=False, default=0)
    card = db.Column(db.Integer, nullable=False, default=0)
    balance = db.Column(db.Integer, nullable=False, default=1000)

    stocks = db.relationship('Purchase_Info', back_populates='user')
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

    users = db.relationship('Purchase_Info', back_populates='stock')

class Purchase_Info(db.Model):
    __tablename__ = 'Purchase_Info'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)

    stock = db.relationship('Stock', back_populates='users')
    user = db.relationship('User', back_populates='stocks')
# db.create_all(extend_existing=True)

class Portfolio(db.Model):
    __tablename__ = 'Portfolio'
    
