from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database import db
from models.account import Account
from models.transaction import Transaction

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    total_balance = sum(a.balance for a in accounts)

    recent_txns = []
    for acc in accounts:
        txns = Transaction.query.filter_by(account_id=acc.id).order_by(
            Transaction.created_at.desc()).limit(5).all()
        recent_txns.extend(txns)

    recent_txns = sorted(recent_txns, key=lambda x: x.created_at, reverse=True)[:10]

    return render_template('dashboard.html',
                           accounts=accounts,
                           total_balance=total_balance,
                           recent_txns=recent_txns)
