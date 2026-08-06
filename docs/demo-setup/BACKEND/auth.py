from functools import wraps
from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash
from models import Customer


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("customer_id"):
            flash("Please log in to access that page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def verify_login(username: str, password: str):
    if not username or not password:
        return None
    customer = Customer.query.filter_by(username=username.strip()).first()
    if customer is None:
        return None
    if not check_password_hash(customer.password_hash, password):
        return None
    return customer
