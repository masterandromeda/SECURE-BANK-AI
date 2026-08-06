from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from datetime import datetime
import random, string

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    otp_sent = None
    if request.method == 'POST':
        step = request.form.get('step', 'credentials')

        if step == 'credentials':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                otp = user.generate_otp()
                session['pre_auth_user_id'] = user.id
                otp_sent = otp
                print(f"\n{'='*40}\n  OTP for {user.email}: {otp}\n{'='*40}\n")
                flash(f'OTP sent! Your OTP is: {otp}', 'info')
                return render_template('login.html', step='otp', otp_display=otp)
            else:
                flash('Invalid email or password.', 'danger')

        elif step == 'otp':
            user_id = session.get('pre_auth_user_id')
            otp_input = request.form.get('otp', '').strip()
            if user_id:
                user = User.query.get(user_id)
                if user and user.mfa_secret == otp_input:
                    user.mfa_secret = None
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    login_user(user)
                    session.pop('pre_auth_user_id', None)
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    return redirect(url_for('dashboard.index'))
                else:
                    flash('Invalid OTP. Please try again.', 'danger')
                    return render_template('login.html', step='otp')

    return render_template('login.html', step='credentials')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        user = User(full_name=full_name, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        acc_number = Account.generate_account_number()
        account = Account(account_number=acc_number, user_id=user.id, balance=10000.0)
        db.session.add(account)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
