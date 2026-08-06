"""Integration tests for all HTTP routes."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

import pytest


def login(client, username="testuser", password="testpass"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


class TestLoginRoute:
    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Login" in resp.data

    def test_valid_login_redirects_to_dashboard(self, client):
        resp = login(client)
        assert resp.status_code == 200
        assert b"Welcome, testuser" in resp.data

    def test_invalid_password_shows_error(self, client):
        resp = client.post("/login", data={"username": "testuser", "password": "wrong"}, follow_redirects=True)
        assert b"Invalid username or password" in resp.data

    def test_empty_username_shows_error(self, client):
        resp = client.post("/login", data={"username": "", "password": "testpass"}, follow_redirects=True)
        assert b"Username is required" in resp.data

    def test_root_redirects_to_login(self, client):
        resp = client.get("/", follow_redirects=True)
        assert b"Login" in resp.data


class TestSessionProtection:
    def test_dashboard_unauthenticated_redirects_to_login(self, client):
        resp = client.get("/dashboard", follow_redirects=True)
        assert b"Login" in resp.data


class TestDashboard:
    def test_dashboard_shows_balance(self, client):
        login(client)
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        assert b"500.00" in resp.data


class TestDepositRoute:
    def test_valid_deposit_increases_balance(self, client):
        login(client)
        resp = client.post("/deposit", data={"amount": "100"}, follow_redirects=True)
        assert b"600.00" in resp.data

    def test_deposit_non_numeric_shows_error(self, client):
        login(client)
        resp = client.post("/deposit", data={"amount": "abc"}, follow_redirects=True)
        assert b"Invalid amount" in resp.data


class TestWithdrawRoute:
    def test_valid_withdrawal_decreases_balance(self, client):
        login(client)
        resp = client.post("/withdraw", data={"amount": "200"}, follow_redirects=True)
        assert b"300.00" in resp.data

    def test_insufficient_funds_shows_error(self, client):
        login(client)
        resp = client.post("/withdraw", data={"amount": "9999"}, follow_redirects=True)
        assert b"Insufficient funds" in resp.data


class TestLogout:
    def test_logout_clears_session_and_redirects(self, client):
        login(client)
        resp = client.post("/logout", follow_redirects=True)
        assert b"Login" in resp.data


class TestErrorPages:
    def test_404_returns_custom_page(self, client):
        resp = client.get("/nonexistent-route")
        assert resp.status_code == 404
        assert b"404" in resp.data
