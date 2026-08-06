from extensions import db
from werkzeug.security import generate_password_hash


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    account = db.relationship("Account", back_populates="customer", uselist=False)

    def __repr__(self):
        return f"<Customer {self.username}>"


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)

    customer = db.relationship("Customer", back_populates="account")

    def __repr__(self):
        return f"<Account customer_id={self.customer_id} balance={self.balance}>"


def init_db():
    db.create_all()

    _seed_users = [
        {"username": "alice", "password": "password123", "balance": 1000.00},
        {"username": "bob",   "password": "secret456",   "balance": 1000.00},
    ]

    for user_data in _seed_users:
        existing = Customer.query.filter_by(username=user_data["username"]).first()
        if existing is None:
            customer = Customer(
                username=user_data["username"],
                password_hash=generate_password_hash(user_data["password"]),
            )
            db.session.add(customer)
            db.session.flush()
            account = Account(customer_id=customer.id, balance=user_data["balance"])
            db.session.add(account)

    db.session.commit()
