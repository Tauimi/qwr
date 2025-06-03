"""
Модель для отслеживания посетителей
"""
from datetime import datetime, timedelta
from my_app.extensions import db
from sqlalchemy import func

class Visitor(db.Model):
    """Модель для отслеживания посетителей"""
    __tablename__ = 'visitors'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    page_visited = db.Column(db.String(255), nullable=True)
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Visitor {self.ip_address}>'

    @classmethod
    def get_visitors_stats(cls):
        """Возвращает статистику посещений"""
        now = datetime.utcnow()
        
        # Общее количество посещений
        total_visits = db.session.query(func.count(cls.id)).scalar()
        
        # Посещения за последние 24 часа
        day_ago = now - timedelta(days=1)
        daily_visits = db.session.query(func.count(cls.id)).filter(cls.visit_time >= day_ago).scalar()
        
        # Посещения за последнюю неделю
        week_ago = now - timedelta(days=7)
        weekly_visits = db.session.query(func.count(cls.id)).filter(cls.visit_time >= week_ago).scalar()
        
        # Посещения за последний месяц
        month_ago = now - timedelta(days=30)
        monthly_visits = db.session.query(func.count(cls.id)).filter(cls.visit_time >= month_ago).scalar()
        
        # Уникальные посетители
        unique_total = db.session.query(func.count(func.distinct(cls.ip_address))).scalar()
        unique_daily = db.session.query(func.count(func.distinct(cls.ip_address))).filter(cls.visit_time >= day_ago).scalar()
        unique_weekly = db.session.query(func.count(func.distinct(cls.ip_address))).filter(cls.visit_time >= week_ago).scalar()
        unique_monthly = db.session.query(func.count(func.distinct(cls.ip_address))).filter(cls.visit_time >= month_ago).scalar()
        
        return {
            'total': total_visits,
            'daily': daily_visits,
            'weekly': weekly_visits,
            'monthly': monthly_visits,
            'unique_total': unique_total,
            'unique_daily': unique_daily,
            'unique_weekly': unique_weekly,
            'unique_monthly': unique_monthly
        } 