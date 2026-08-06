from extensions import db
from models import Account


def deposit(customer_id: int, amount: float) -> dict:
    if amount <= 0:
        return {"success": False, "message": "Deposit amount must be greater than zero.", "balance": None}
    account = Account.query.filter_by(customer_id=customer_id).first()
    if account is None:
        return {"success": False, "message": "Account not found.", "balance": None}
    account.balance = round(account.balance + amount, 2)
    db.session.commit()
    return {"success": True, "message": f"Successfully deposited ${amount:.2f}.", "balance": account.balance}


def withdraw(customer_id: int, amount: float) -> dict:
    if amount <= 0:
        return {"success": False, "message": "Withdrawal amount must be greater than zero.", "balance": None}
    account = Account.query.filter_by(customer_id=customer_id).first()
    if account is None:
        return {"success": False, "message": "Account not found.", "balance": None}
    if amount > account.balance:
        return {"success": False, "message": "Insufficient funds.", "balance": account.balance}
    account.balance = round(account.balance - amount, 2)
    db.session.commit()
    return {"success": True, "message": f"Successfully withdrew ${amount:.2f}.", "balance": account.balance}
