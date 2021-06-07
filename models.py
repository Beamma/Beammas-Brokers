from main import db
#
#
# PizzaTopping = db.Table('PizzaTopping', db.Model.metadata,
#                     db.Column('Pizza_id', db.Integer, db.ForeignKey('Pizza.id')),
#                     db.Column('Topping_id', db.Integer, db.ForeignKey('Topping.id'))
#                    )
#
#
# class Pizza(db.Model):
#   __tablename__ = 'Pizza'
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String())
#   description = db.Column(db.String())
#
#   toppings = db.relationship('Topping', secondary=PizzaTopping, back_populates='pizzas')
#
#
# class Topping(db.Model):
#   __tablename__ = 'Topping'
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String())
#   description = db.Column(db.String())
#
#   pizzas = db.relationship('Pizza', secondary=PizzaTopping, back_populates='toppings')

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    pass_word = db.Column(db.String(), nullable=False)
    ird = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(), nullable=False)
    bank = db.Column(db.Integer, nullable=False, default=0)
    card = db.Column(db.Integer, nullable=False, default=0)
    balance = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<User {self.name}>'
# db.create_all(extend_existing=True)
