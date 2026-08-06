# 🏦 SECURE BANK AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A cybersecurity-themed full-stack banking platform powered by SENTINEL AI**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Quick Start](#-quick-start) • [Project Structure](#-project-structure) • [Screenshots](#-screenshots)

</div>

---

## 🔐 Overview

**SecureBank AI** is a full-stack banking web application built with Flask and designed around a **cybersecurity-first** philosophy. It features a real-time AI threat monitoring agent (SENTINEL), fraud detection, UPI/QR payments, multi-factor authentication, an encrypted document vault, and RBI compliance awareness — all wrapped in a sleek dark cyber-themed UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🛡️ **SENTINEL AI Agent** | Real-time radar-based threat monitoring with live blip rendering and 4-second refresh |
| 🔑 **MFA / OTP Login** | Two-step authentication — password + OTP (shown in console for demo) |
| 💸 **Full Banking Suite** | Deposit, Withdraw, Fund Transfer, UPI/QR Pay |
| 📊 **Spend Analytics** | Credit/Debit breakdown with transaction history |
| 🚨 **Fraud Intelligence** | Flagged transaction dashboard with fraud score tracking |
| 🗄️ **Secure Document Vault** | AES-256 encrypted document storage (Aadhaar, PAN, Passport, etc.) |
| 👤 **Profile & KYC** | User profile management with KYC status tracking |
| 🏛️ **RBI Compliance** | Fraud awareness guide with common scam types and helpline numbers |
| 🔒 **Privacy Dashboard** | Transparent data handling overview |
| 📱 **Responsive UI** | Mobile-friendly dark cyber theme |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Flask 3.1.3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite (auto-created on first run)
- **Frontend:** Jinja2 Templates, Bootstrap 5.3, Font Awesome 6.4, Custom Cyber CSS
- **Security:** Werkzeug password hashing, CSRF protection, session-based MFA
- **AI Agent:** Custom heuristic threat scoring with radar visualization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/masterandromeda/SECURE-BANK-AI.git
cd SECURE-BANK-AI/SecureBankAI
```

### 2. Create and activate virtual environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🔑 Demo Credentials

| Field | Value |
|---|---|
| **Email** | `demo@securebankai.in` |
| **Password** | `Demo@123` |
| **OTP** | Printed in the console on login |

> The demo account is auto-seeded on first run with ₹2,50,000 balance.

---

## 📁 Project Structure

```
SECURE-BANK-AI/
│
├── SecureBankAI/                  ← Main Flask application
│   ├── app.py                     ← App factory + seed
│   ├── config.py                  ← Configuration
│   ├── database.py                ← SQLAlchemy, LoginManager, CSRF
│   ├── requirements.txt           ← Python dependencies
│   │
│   ├── models/                    ← SQLAlchemy ORM models
│   │   ├── user.py                ← User model + OTP generation
│   │   ├── account.py             ← Bank account model
│   │   ├── transaction.py         ← Transaction model with fraud fields
│   │   └── document.py            ← KYC document model
│   │
│   ├── routes/                    ← Flask Blueprints
│   │   ├── auth.py                ← Login, Register, Logout (MFA)
│   │   ├── dashboard.py           ← Live dashboard
│   │   ├── banking.py             ← Deposit, Withdraw, Transfer, UPI
│   │   ├── analytics.py           ← Spend analytics
│   │   ├── security.py            ← Security center, Fraud dashboard, Vault
│   │   ├── profile.py             ← Profile & KYC management
│   │   ├── privacy.py             ← Privacy dashboard
│   │   └── agent.py               ← SENTINEL AI API endpoints
│   │
│   ├── templates/                 ← Jinja2 HTML templates (cyber dark theme)
│   │   ├── base.html              ← Master layout with sidebar + topbar
│   │   ├── login.html             ← MFA login with risk panel
│   │   ├── dashboard.html         ← Live command center with radar
│   │   ├── accounts.html          ← Account management
│   │   ├── deposit.html           ← Deposit funds
│   │   ├── withdraw.html          ← Withdraw funds
│   │   ├── transfer.html          ← Fund transfer
│   │   ├── upi.html               ← UPI + QR camera scanner
│   │   ├── transactions.html      ← Full transaction log
│   │   ├── analytics.html         ← Spend analytics
│   │   ├── fraud_dashboard.html   ← Flagged transactions
│   │   ├── security.html          ← Security center
│   │   ├── vault.html             ← Encrypted document vault
│   │   ├── rbi_awareness.html     ← RBI fraud awareness
│   │   ├── privacy.html           ← Privacy dashboard
│   │   ├── profile.html           ← User profile & KYC
│   │   └── errors/                ← 404 & 500 error pages
│   │
│   └── static/
│       ├── css/main.css           ← Full cyber dark theme stylesheet
│       └── js/main.js             ← SENTINEL radar, QR scanner, clock
│
└── docs/demo-setup/               ← Simpler demo/reference implementation
    ├── BACKEND/                   ← Minimal Flask backend
    ├── FRONTEND/                  ← Basic templates
    ├── tests/                     ← Full pytest test suite
    ├── requirements.txt
    ├── README.md
    ├── banking-app-plan.md
    └── IMPLEMENTATION_PLAN.md
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/agent/status` | SENTINEL threat score + radar blips (auth required) |
| POST | `/api/agent/login-risk` | Login risk assessment (public) |

---

## 🔒 Security Notes

- Passwords hashed with Werkzeug's `pbkdf2:sha256`
- CSRF protection on all forms via Flask-WTF
- Session cookies: `HttpOnly`, `SameSite=Lax`
- MFA enforced on every login
- No sensitive data stored in session beyond `user_id`
- For production: set `SECRET_KEY` via environment variable, set `DEBUG=False`, use Gunicorn/Waitress

---

## 🧪 Running Tests (Demo Setup)

```bash
cd docs/demo-setup
pip install -r requirements.txt
pytest tests/
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">
Made with ❤️ — SecureBank AI · SENTINEL Security Platform · India
</div>
