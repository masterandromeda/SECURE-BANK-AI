from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from database import db, csrf
from models.user import User
from models.account import Account
from models.transaction import Transaction
from datetime import datetime, timedelta, date
import random, string, re, secrets

auth = Blueprint('auth', __name__)

# ── OTP store (in-memory for demo; keyed by target) ─────────────────────────
# Structure: { 'phone:9876543210': {'otp': '123456', 'expires': datetime} }
_otp_store: dict = {}

_OTP_TTL_MINUTES = 10


def _generate_otp() -> str:
    """Cryptographically secure 6-digit OTP."""
    return str(secrets.randbelow(900000) + 100000)


def _store_otp(key: str, otp: str) -> None:
    _otp_store[key] = {
        'otp': otp,
        'expires': datetime.utcnow() + timedelta(minutes=_OTP_TTL_MINUTES),
    }


def _verify_otp(key: str, submitted: str) -> bool:
    entry = _otp_store.get(key)
    if not entry:
        return False
    if datetime.utcnow() > entry['expires']:
        _otp_store.pop(key, None)
        return False
    if entry['otp'] != submitted.strip():
        return False
    _otp_store.pop(key, None)   # single-use
    return True


def _mock_send_sms(phone: str, otp: str) -> None:
    """Mock SMS provider — prints to console (replace with Twilio/MSG91)."""
    print(f"\n{'='*50}")
    print(f"  [MOCK SMS] To: +91{phone}  |  OTP: {otp}")
    print(f"  Expires in {_OTP_TTL_MINUTES} minutes")
    print(f"{'='*50}\n")


def _mock_send_email(email: str, otp: str) -> None:
    """Mock email provider — prints to console (replace with SMTP/SendGrid)."""
    print(f"\n{'='*50}")
    print(f"  [MOCK EMAIL] To: {email}  |  OTP: {otp}")
    print(f"  Expires in {_OTP_TTL_MINUTES} minutes")
    print(f"{'='*50}\n")


# ── Password strength validator ──────────────────────────────────────────────
def _validate_password(pw: str) -> list:
    errors = []
    if len(pw) < 12:
        errors.append('At least 12 characters required.')
    if not re.search(r'[A-Z]', pw):
        errors.append('At least one uppercase letter required.')
    if not re.search(r'[a-z]', pw):
        errors.append('At least one lowercase letter required.')
    if not re.search(r'\d', pw):
        errors.append('At least one digit required.')
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', pw):
        errors.append('At least one special character required.')
    return errors


# ── Field validators ─────────────────────────────────────────────────────────
def _validate_phone(phone: str) -> str | None:
    phone = re.sub(r'\D', '', phone)
    if not re.fullmatch(r'[6-9]\d{9}', phone):
        return 'Enter a valid 10-digit Indian mobile number.'
    return None


def _validate_email(email: str) -> str | None:
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return 'Enter a valid email address.'
    return None


def _validate_aadhaar(aadhaar: str) -> str | None:
    aadhaar = re.sub(r'\s', '', aadhaar)
    if not re.fullmatch(r'\d{12}', aadhaar):
        return 'Aadhaar must be exactly 12 digits.'
    return None


def _validate_pan(pan: str) -> str | None:
    if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', pan.upper()):
        return 'PAN must be in format: ABCDE1234F'
    return None


def _validate_dob(dob: str) -> str | None:
    try:
        d = datetime.strptime(dob, '%Y-%m-%d')
        age = (datetime.utcnow() - d).days // 365
        if age < 18:
            return 'You must be at least 18 years old.'
        if age > 100:
            return 'Enter a valid date of birth.'
    except ValueError:
        return 'Enter a valid date of birth (YYYY-MM-DD).'
    return None


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


# ── OTP API: send mobile OTP ─────────────────────────────────────────────────
@auth.route('/api/register/send-mobile-otp', methods=['POST'])
@csrf.exempt
def send_mobile_otp():
    data = request.get_json(silent=True) or {}
    phone = re.sub(r'\D', '', data.get('phone', ''))
    err = _validate_phone(phone)
    if err:
        return jsonify({'success': False, 'message': err}), 400
    if User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': 'Mobile number already registered.'}), 400
    otp = _generate_otp()
    _store_otp(f'phone:{phone}', otp)
    _mock_send_sms(phone, otp)
    # Return OTP in response only for demo — remove in production
    return jsonify({'success': True, 'message': f'OTP sent to +91{phone}', 'demo_otp': otp})


# ── OTP API: verify mobile OTP ────────────────────────────────────────────────
@auth.route('/api/register/verify-mobile-otp', methods=['POST'])
@csrf.exempt
def verify_mobile_otp():
    data = request.get_json(silent=True) or {}
    phone = re.sub(r'\D', '', data.get('phone', ''))
    otp   = data.get('otp', '').strip()
    if not _verify_otp(f'phone:{phone}', otp):
        return jsonify({'success': False, 'message': 'Invalid or expired OTP.'}), 400
    # Store verified flag in session
    session[f'mobile_verified_{phone}'] = True
    return jsonify({'success': True, 'message': 'Mobile number verified!'})


# ── OTP API: send email OTP ───────────────────────────────────────────────────
@auth.route('/api/register/send-email-otp', methods=['POST'])
@csrf.exempt
def send_email_otp():
    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    err = _validate_email(email)
    if err:
        return jsonify({'success': False, 'message': err}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered.'}), 400
    otp = _generate_otp()
    _store_otp(f'email:{email}', otp)
    _mock_send_email(email, otp)
    return jsonify({'success': True, 'message': f'OTP sent to {email}', 'demo_otp': otp})


# ── OTP API: verify email OTP ─────────────────────────────────────────────────
@auth.route('/api/register/verify-email-otp', methods=['POST'])
@csrf.exempt
def verify_email_otp():
    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    otp   = data.get('otp', '').strip()
    if not _verify_otp(f'email:{email}', otp):
        return jsonify({'success': False, 'message': 'Invalid or expired OTP.'}), 400
    session[f'email_verified_{email}'] = True
    return jsonify({'success': True, 'message': 'Email address verified!'})


# ── Registration form ─────────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        phone     = re.sub(r'\D', '', request.form.get('phone', ''))
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')
        aadhaar   = re.sub(r'\s', '', request.form.get('aadhaar_number', ''))
        pan       = request.form.get('pan_number', '').strip().upper()
        dob       = request.form.get('date_of_birth', '').strip()
        address   = request.form.get('address', '').strip()

        errors = []

        # ── Required field checks ──────────────────────────────────────────
        if not full_name or len(full_name) < 3:
            errors.append('Full name must be at least 3 characters.')
        if not re.fullmatch(r'[A-Za-z ]{3,100}', full_name):
            errors.append('Full name must contain only letters and spaces.')

        phone_err = _validate_phone(phone)
        if phone_err:
            errors.append(phone_err)

        email_err = _validate_email(email)
        if email_err:
            errors.append(email_err)

        pw_errors = _validate_password(password)
        errors.extend(pw_errors)

        if password != confirm:
            errors.append('Passwords do not match.')

        aadhaar_err = _validate_aadhaar(aadhaar)
        if aadhaar_err:
            errors.append(aadhaar_err)

        pan_err = _validate_pan(pan)
        if pan_err:
            errors.append(pan_err)

        dob_err = _validate_dob(dob)
        if dob_err:
            errors.append(dob_err)

        if not address or len(address) < 10:
            errors.append('Please enter a complete residential address (min 10 characters).')

        # ── OTP verification gate ──────────────────────────────────────────
        if not session.get(f'mobile_verified_{phone}'):
            errors.append('Mobile number OTP verification is required.')

        if not session.get(f'email_verified_{email}'):
            errors.append('Email address OTP verification is required.')

        # ── Uniqueness checks ──────────────────────────────────────────────
        if not errors:
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')
            if User.query.filter_by(phone=phone).first():
                errors.append('Mobile number already registered.')
            if User.query.filter_by(aadhar_number=aadhaar).first():
                errors.append('Aadhaar number already registered.')
            if User.query.filter_by(pan_number=pan).first():
                errors.append('PAN number already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', now_date=date.today().isoformat())

        # ── Create user ────────────────────────────────────────────────────
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            date_of_birth=dob,
            aadhar_number=aadhaar,
            pan_number=pan,
            kyc_status='pending',
            is_verified=False,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        acc_number = Account.generate_account_number()
        account = Account(account_number=acc_number, user_id=user.id, balance=10000.0)
        db.session.add(account)
        db.session.commit()

        # Clear verification session keys
        session.pop(f'mobile_verified_{phone}', None)
        session.pop(f'email_verified_{email}', None)

        flash('Registration successful! Your account is under KYC review. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', now_date=date.today().isoformat())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
