from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.transaction import Transaction
from models.account import Account

security = Blueprint('security', __name__)

@security.route('/security')
@login_required
def index():
    return render_template('security.html')

@security.route('/fraud-dashboard')
@login_required
def fraud_dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    account_ids = [a.id for a in accounts]
    flagged_txns = Transaction.query.filter(
        Transaction.account_id.in_(account_ids),
        Transaction.is_flagged == True
    ).order_by(Transaction.created_at.desc()).all()
    return render_template('fraud_dashboard.html', flagged_txns=flagged_txns)

@security.route('/vault')
@login_required
def vault():
    return render_template('vault.html')

@security.route('/rbi-awareness')
@login_required
def rbi_awareness():
    return render_template('rbi_awareness.html')
