from routes.auth import auth
from routes.dashboard import dashboard_bp
from routes.banking import banking
from routes.security import security
from routes.profile import profile
from routes.analytics import analytics
from routes.privacy import privacy
from routes.agent import agent_bp

def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(banking)
    app.register_blueprint(security)
    app.register_blueprint(profile)
    app.register_blueprint(analytics)
    app.register_blueprint(privacy)
    app.register_blueprint(agent_bp)
