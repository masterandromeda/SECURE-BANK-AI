from flask import Blueprint, render_template
from flask_login import login_required

privacy = Blueprint('privacy', __name__)

@privacy.route('/privacy')
@login_required
def index():
    return render_template('privacy.html')
