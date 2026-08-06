from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.transaction import Transaction
from models.account import Account

analytics = Blueprint('analytics', __name__)

@analytics.route('/analytics')
@login_required
def index():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    account_ids = [a.id for a in accounts]
    txns = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(
        Transaction.created_at.desc()).limit(100).all()
    credits = sum(t.amount for t in txns if t.transaction_type == 'credit')
    debits = sum(t.amount for t in txns if t.transaction_type == 'debit')
    return render_template('analytics.html', txns=txns, credits=credits, debits=debits)
