from database import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    mfa_secret = db.Column(db.String(6), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.String(20), nullable=True)
    pan_number = db.Column(db.String(10), nullable=True)
    aadhar_number = db.Column(db.String(12), nullable=True)
    kyc_status = db.Column(db.String(20), default='pending')

    accounts = db.relationship('Account', backref='owner', lazy=True)
    documents = db.relationship('Document', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=6))
        self.mfa_secret = otp
        db.session.commit()
        return otp

    def __repr__(self):
        return f'<User {self.email}>'
