# SecureBank AI — Demo Setup (Reference Implementation)

A simpler, minimal Flask banking app used as the demo/reference implementation alongside the main SecureBank AI project.

## Setup

```bash
cd docs/demo-setup
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cd BACKEND
flask --app app run
```

Open: http://127.0.0.1:5000

## Test Credentials

| Username | Password    | Balance    |
|----------|-------------|------------|
| alice    | password123 | $1,000.00  |
| bob      | secret456   | $1,000.00  |

## Run Tests

```bash
pytest tests/
```
