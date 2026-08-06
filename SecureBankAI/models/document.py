from database import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    doc_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Document {self.doc_type} - {self.user_id}>'
