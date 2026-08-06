from database import db
from datetime import datetime
import random
import string

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), unique=True, nullable=False)
    account_type = db.Column(db.String(20), default='savings')
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ifsc_code = db.Column(db.String(11), default='SBIN0001234')
    branch = db.Column(db.String(100), default='Mumbai Main Branch')

    transactions = db.relationship('Transaction', backref='account', lazy=True,
                                   foreign_keys='Transaction.account_id')

    @staticmethod
    def generate_account_number():
        return ''.join(random.choices(string.digits, k=16))

    def __repr__(self):
        return f'<Account {self.account_number}>'
