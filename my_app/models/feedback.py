
"""
Модель для сообщений обратной связи
"""
from datetime import datetime
from my_app.extensions import db

class FeedbackMessage(db.Model):
    """Модель для сообщений обратной связи"""
    __tablename__ = 'feedback_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<FeedbackMessage {self.id}: {self.subject}>'
