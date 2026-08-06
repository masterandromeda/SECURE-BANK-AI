from flask import Flask, render_template
from config import Config
from database import db, login_manager, csrf, init_extensions
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)

    with app.app_context():
        from models.user import User
        from models.account import Account
        from models.transaction import Transaction
        from models.document import Document

        db.create_all()
        register_blueprints(app)
        seed_demo_user(app)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app

def seed_demo_user(app):
    from models.user import User
    from models.account import Account

    if not User.query.filter_by(email='demo@securebankai.in').first():
        user = User(
            full_name='Demo User',
            email='demo@securebankai.in',
            phone='9876543210',
            is_verified=True,
            kyc_status='verified'
        )
        user.set_password('Demo@123')
        db.session.add(user)
        db.session.flush()

        account = Account(
            account_number='1234567890123456',
            account_type='savings',
            balance=250000.0,
            user_id=user.id
        )
        db.session.add(account)
        db.session.commit()
        print("[OK] Demo user created: demo@securebankai.in / Demo@123")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
