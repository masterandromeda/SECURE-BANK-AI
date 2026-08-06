from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.account import Account
from models.transaction import Transaction
from datetime import datetime
import random, string

banking = Blueprint('banking', __name__)

def generate_ref():
    return 'REF' + ''.join(random.choices(string.digits, k=10))

@banking.route('/accounts')
@login_required
def accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@banking.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', 'Cash Deposit')

        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Invalid account.', 'danger')
            return redirect(url_for('banking.deposit'))

        if amount <= 0:
            flash('Amount must be greater than zero.', 'danger')
            return redirect(url_for('banking.deposit'))

        account.balance += amount
        txn = Transaction(
            account_id=account.id,
            transaction_type='credit',
            category='deposit',
            amount=amount,
            balance_after=account.balance,
            description=description,
            reference_number=generate_ref()
        )
        db.session.add(txn)
        db.session.commit()
        flash(f'\u20b9{amount:,.2f} deposited successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('deposit.html', accounts=accounts)

@banking.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', 'Cash Withdrawal')

        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Invalid account.', 'danger')
            return redirect(url_for('banking.withdraw'))

        if amount <= 0 or amount > account.balance:
            flash('Invalid amount or insufficient balance.', 'danger')
            return redirect(url_for('banking.withdraw'))

        account.balance -= amount
        txn = Transaction(
            account_id=account.id,
            transaction_type='debit',
            category='withdrawal',
            amount=amount,
            balance_after=account.balance,
            description=description,
            reference_number=generate_ref()
        )
        db.session.add(txn)
        db.session.commit()
        flash(f'\u20b9{amount:,.2f} withdrawn successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('withdraw.html', accounts=accounts)

@banking.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id')
        to_account_number = request.form.get('to_account_number', '').strip()
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', 'Fund Transfer')

        from_account = Account.query.filter_by(id=from_account_id, user_id=current_user.id).first()
        to_account = Account.query.filter_by(account_number=to_account_number).first()

        if not from_account:
            flash('Invalid source account.', 'danger')
            return redirect(url_for('banking.transfer'))

        if not to_account:
            flash('Recipient account not found.', 'danger')
            return redirect(url_for('banking.transfer'))

        if amount <= 0 or amount > from_account.balance:
            flash('Invalid amount or insufficient balance.', 'danger')
            return redirect(url_for('banking.transfer'))

        from_account.balance -= amount
        to_account.balance += amount
        ref = generate_ref()

        debit_txn = Transaction(
            account_id=from_account.id,
            transaction_type='debit',
            category='transfer',
            amount=amount,
            balance_after=from_account.balance,
            description=description,
            reference_number=ref,
            recipient_account=to_account_number,
            recipient_name=to_account.owner.full_name
        )
        credit_txn = Transaction(
            account_id=to_account.id,
            transaction_type='credit',
            category='transfer',
            amount=amount,
            balance_after=to_account.balance,
            description=f'Transfer from {from_account.account_number}',
            reference_number='IN' + ref
        )
        db.session.add_all([debit_txn, credit_txn])
        db.session.commit()
        flash(f'\u20b9{amount:,.2f} transferred successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('transfer.html', accounts=accounts)

@banking.route('/transactions')
@login_required
def transactions():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    account_ids = [a.id for a in accounts]
    txns = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(
        Transaction.created_at.desc()).limit(50).all()
    return render_template('transactions.html', transactions=txns, accounts=accounts)

@banking.route('/upi', methods=['GET', 'POST'])
@login_required
def upi():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    if request.method == 'POST':
        upi_id = request.form.get('upi_id', '').strip()
        amount = float(request.form.get('amount', 0))
        account_id = request.form.get('account_id')
        note = request.form.get('note', 'UPI Payment')

        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account or amount <= 0 or amount > account.balance:
            flash('Invalid account or insufficient balance.', 'danger')
            return redirect(url_for('banking.upi'))

        account.balance -= amount
        txn = Transaction(
            account_id=account.id,
            transaction_type='debit',
            category='upi',
            amount=amount,
            balance_after=account.balance,
            description=f'UPI to {upi_id}: {note}',
            reference_number=generate_ref(),
            recipient_account=upi_id
        )
        db.session.add(txn)
        db.session.commit()
        flash(f'\u20b9{amount:,.2f} sent to {upi_id} via UPI!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('upi.html', accounts=accounts)
