import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

import pytest
from app import create_app, db as _db
from models import Customer, Account, init_db
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="function")
def app():
    application = create_app(testing=True)
    with application.app_context():
        _db.create_all()
        customer = Customer(
            username="testuser",
            password_hash=generate_password_hash("testpass"),
        )
        _db.session.add(customer)
        _db.session.flush()
        account = Account(customer_id=customer.id, balance=500.00)
        _db.session.add(account)
        _db.session.commit()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
