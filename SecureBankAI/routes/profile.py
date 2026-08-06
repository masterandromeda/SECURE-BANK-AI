from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.user import User
from models.document import Document

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        current_user.date_of_birth = request.form.get('date_of_birth', current_user.date_of_birth)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))
    return render_template('profile.html')

@profile.route('/kyc', methods=['GET', 'POST'])
@login_required
def kyc():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        doc_type = request.form.get('doc_type')
        doc_name = request.form.get('doc_name', doc_type)
        doc = Document(user_id=current_user.id, doc_type=doc_type, doc_name=doc_name)
        db.session.add(doc)
        db.session.commit()
        flash('Document submitted for verification.', 'success')
        return redirect(url_for('profile.kyc'))
    return render_template('profile.html', documents=documents)
