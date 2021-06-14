from main import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    ird = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(), nullable=False)
    bank = db.Column(db.Integer, nullable=False, default=0)
    card = db.Column(db.Integer, nullable=False, default=0)
    balance = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<User {self.id, self.name, self.email, self.password, self.ird, self.address, self.bank, self.card, self.balance}>'

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    logo = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    symbol = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), nullable=False)
    market = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(), nullable=False)

# db.create_all(extend_existing=True)
