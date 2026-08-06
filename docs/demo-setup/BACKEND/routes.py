from flask import flash, redirect, render_template, request, session, url_for
from extensions import db
from auth import login_required, verify_login
from models import Account, Customer
from transactions import deposit, withdraw


def register_routes(app):
    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("customer_id"):
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username:
                flash("Username is required.", "danger")
                return render_template("login.html")
            if not password:
                flash("Password is required.", "danger")
                return render_template("login.html")
            customer = verify_login(username, password)
            if customer is None:
                flash("Invalid username or password.", "danger")
                return render_template("login.html")
            session["customer_id"] = customer.id
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        customer_id = session["customer_id"]
        customer = db.session.get(Customer, customer_id)
        account = Account.query.filter_by(customer_id=customer_id).first()
        return render_template("dashboard.html", username=customer.username, balance=account.balance)

    @app.route("/deposit", methods=["GET", "POST"])
    @login_required
    def deposit_route():
        customer_id = session["customer_id"]
        account = Account.query.filter_by(customer_id=customer_id).first()
        if request.method == "POST":
            raw_amount = request.form.get("amount", "")
            try:
                amount = float(raw_amount)
            except ValueError:
                flash("Invalid amount entered. Please enter a valid number.", "danger")
                return render_template("deposit.html", balance=account.balance)
            result = deposit(customer_id, amount)
            if result["success"]:
                flash(result["message"], "success")
            else:
                flash(result["message"], "danger")
                return render_template("deposit.html", balance=account.balance)
            return redirect(url_for("dashboard"))
        return render_template("deposit.html", balance=account.balance)

    @app.route("/withdraw", methods=["GET", "POST"])
    @login_required
    def withdraw_route():
        customer_id = session["customer_id"]
        account = Account.query.filter_by(customer_id=customer_id).first()
        if request.method == "POST":
            raw_amount = request.form.get("amount", "")
            try:
                amount = float(raw_amount)
            except ValueError:
                flash("Invalid amount entered. Please enter a valid number.", "danger")
                return render_template("withdraw.html", balance=account.balance)
            result = withdraw(customer_id, amount)
            if result["success"]:
                flash(result["message"], "success")
            else:
                flash(result["message"], "danger")
                return render_template("withdraw.html", balance=account.balance)
            return redirect(url_for("dashboard"))
        return render_template("withdraw.html", balance=account.balance)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500
