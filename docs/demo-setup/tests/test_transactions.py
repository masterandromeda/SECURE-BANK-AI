"""Unit tests for BACKEND/transactions.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

import pytest
from models import Customer, Account
from transactions import deposit, withdraw


class TestDeposit:
    def test_valid_deposit_increases_balance(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = deposit(cid, 100.00)
            assert result["success"] is True
            assert result["balance"] == 600.00

    def test_deposit_zero_returns_failure(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = deposit(cid, 0)
            assert result["success"] is False
            assert "greater than zero" in result["message"]

    def test_deposit_negative_returns_failure(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = deposit(cid, -50.00)
            assert result["success"] is False

    def test_deposit_fractional_amount(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = deposit(cid, 0.01)
            assert result["success"] is True
            assert result["balance"] == 500.01


class TestWithdraw:
    def test_valid_withdrawal_decreases_balance(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = withdraw(cid, 200.00)
            assert result["success"] is True
            assert result["balance"] == 300.00

    def test_exact_balance_withdrawal_succeeds(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = withdraw(cid, 500.00)
            assert result["success"] is True
            assert result["balance"] == 0.00

    def test_withdrawal_exceeds_balance_returns_failure(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = withdraw(cid, 999.00)
            assert result["success"] is False
            assert "Insufficient funds" in result["message"]
            account = Account.query.filter_by(customer_id=cid).first()
            assert account.balance == 500.00

    def test_withdrawal_zero_returns_failure(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = withdraw(cid, 0)
            assert result["success"] is False

    def test_withdrawal_negative_returns_failure(self, app):
        with app.app_context():
            cid = Customer.query.filter_by(username="testuser").first().id
            result = withdraw(cid, -100.00)
            assert result["success"] is False
