from main import db


PizzaTopping = db.Table('PizzaTopping', db.Model.metadata,
                    db.Column('Pizza_id', db.Integer, db.ForeignKey('Pizza.id')),
                    db.Column('Topping_id', db.Integer, db.ForeignKey('Topping.id'))
                   )


class Pizza(db.Model):
  __tablename__ = 'Pizza'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  description = db.Column(db.String())

  toppings = db.relationship('Topping', secondary=PizzaTopping, back_populates='pizzas')


class Topping(db.Model):
  __tablename__ = 'Topping'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  description = db.Column(db.String())

  pizzas = db.relationship('Pizza', secondary=PizzaTopping, back_populates='toppings')
