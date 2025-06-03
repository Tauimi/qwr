
"""
Модель для хранения голосов за отзывы
"""
from my_app.extensions import db

class ReviewVote(db.Model):
    """Модель для хранения голосов за отзывы"""
    __tablename__ = 'review_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(50))  # Для неавторизованных пользователей
    vote_type = db.Column(db.String(10), nullable=False)  # 'like' или 'dislike'
    
    # Связи с другими моделями
    review = db.relationship('Review', backref=db.backref('votes', lazy=True))
    user = db.relationship('User', backref=db.backref('review_votes', lazy=True))
    
    def __repr__(self):
        return f'<ReviewVote {self.id}: {self.vote_type}>'
