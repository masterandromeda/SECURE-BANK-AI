"""Unit tests for BACKEND/auth.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

import pytest
from auth import verify_login


class TestVerifyLogin:
    def test_correct_credentials_returns_customer(self, app):
        with app.app_context():
            customer = verify_login("testuser", "testpass")
            assert customer is not None
            assert customer.username == "testuser"

    def test_wrong_password_returns_none(self, app):
        with app.app_context():
            result = verify_login("testuser", "wrongpassword")
            assert result is None

    def test_unknown_username_returns_none(self, app):
        with app.app_context():
            result = verify_login("nobody", "testpass")
            assert result is None

    def test_empty_username_returns_none(self, app):
        with app.app_context():
            result = verify_login("", "testpass")
            assert result is None

    def test_empty_password_returns_none(self, app):
        with app.app_context():
            result = verify_login("testuser", "")
            assert result is None
