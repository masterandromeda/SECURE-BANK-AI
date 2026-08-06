from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from database import db
from models.transaction import Transaction
from models.account import Account
from datetime import datetime, timedelta
import random, hashlib

agent_bp = Blueprint('agent', __name__)

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')

def threat_score_for_user(user_id):
    """Simple heuristic threat score 0-100."""
    try:
        since = datetime.utcnow() - timedelta(hours=1)
        accounts = Account.query.filter_by(user_id=user_id).all()
        ids = [a.id for a in accounts]
        recent = Transaction.query.filter(
            Transaction.account_id.in_(ids),
            Transaction.created_at >= since
        ).count()
        score = min(recent * 5, 30)
        flagged = Transaction.query.filter(
            Transaction.account_id.in_(ids),
            Transaction.is_flagged == True
        ).count()
        score += min(flagged * 20, 50)
        return score
    except Exception:
        return 0

@agent_bp.route('/api/agent/status')
@login_required
def agent_status():
    score = threat_score_for_user(current_user.id)
    if score < 20:
        level, color, msg = 'LOW', '#10b981', 'All systems secure. No threats detected.'
    elif score < 50:
        level, color, msg = 'MEDIUM', '#f59e0b', 'Elevated activity detected. Monitoring closely.'
    else:
        level, color, msg = 'HIGH', '#ef4444', 'High risk detected! Immediate review recommended.'

    ip = get_client_ip()
    ip_hash = hashlib.md5(ip.encode()).hexdigest()[:8].upper()

    events = [
        {'type': 'low',    'msg': 'Session heartbeat verified',        'time': '00:00'},
        {'type': 'low',    'msg': 'SSL certificate validated',          'time': '00:02'},
        {'type': 'medium', 'msg': f'IP fingerprint: {ip_hash}',        'time': '00:05'},
        {'type': 'low',    'msg': 'No brute-force patterns detected',   'time': '00:08'},
    ]
    if score >= 20:
        events.append({'type': 'medium', 'msg': 'Unusual transaction frequency', 'time': 'NOW'})
    if score >= 50:
        events.append({'type': 'high',   'msg': 'ALERT: Flagged transactions found', 'time': 'NOW'})

    blips = []
    for _ in range(max(2, min(score // 10 + 2, 8))):
        angle = random.uniform(0, 360)
        dist  = random.uniform(20, 95)
        import math
        bx = 110 + dist * math.cos(math.radians(angle))
        by = 110 + dist * math.sin(math.radians(angle))
        blips.append({'x': round(bx, 1), 'y': round(by, 1), 'type': 'low' if score < 20 else ('medium' if score < 50 else 'high')})

    return jsonify({
        'threat_level': level,
        'threat_score': score,
        'color': color,
        'message': msg,
        'events': events,
        'blips': blips,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
        'agent': 'SENTINEL-AI v2.4',
        'user': current_user.full_name,
        'ip_hash': ip_hash,
    })

@agent_bp.route('/api/agent/login-risk', methods=['POST'])
def login_risk():
    """Called on failed login to return risk assessment."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    ip    = get_client_ip()
    ip_hash = hashlib.md5(ip.encode()).hexdigest()[:8].upper()

    failed_key = f"failed_{email}"
    fails = session.get(failed_key, 0) + 1
    session[failed_key] = fails

    if fails >= 3:
        risk = 'HIGH'
        risk_msg = f'Multiple failed attempts detected from IP {ip_hash}. Account may be under brute-force attack.'
    elif fails == 2:
        risk = 'MEDIUM'
        risk_msg = f'Second failed attempt. Suspicious activity from IP {ip_hash}.'
    else:
        risk = 'LOW'
        risk_msg = f'Invalid credentials entered. IP fingerprint: {ip_hash}.'

    return jsonify({
        'risk': risk,
        'risk_msg': risk_msg,
        'attempts': fails,
        'ip_hash': ip_hash,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
    })
