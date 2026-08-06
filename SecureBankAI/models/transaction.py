from database import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    reference_number = db.Column(db.String(20), unique=True, nullable=False)
    recipient_account = db.Column(db.String(16), nullable=True)
    recipient_name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='success')
    is_flagged = db.Column(db.Boolean, default=False)
    fraud_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.reference_number}>'
