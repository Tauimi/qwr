"""
Модели товаров и спецификаций
"""
from datetime import datetime
from my_app.extensions import db

class Specification(db.Model):
    """Модель спецификаций товара"""
    __tablename__ = 'specifications'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Specification {self.name}: {self.value}>'

class Product(db.Model):
    """Модель товара"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    sku = db.Column(db.String(50), nullable=True, default=None)  # Артикул товара с явным default=None
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=True, default='default-product.jpg')
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_sale = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    specifications = db.relationship('Specification', backref='product', lazy=True, cascade='all, delete-orphan')
    # 'ratings' уже должно быть доступно через backref из модели Rating

    @property
    def discount_percent(self):
        """Вычисляет процент скидки, если есть старая цена"""
        if self.old_price and self.old_price > self.price:
            return int(100 - (self.price / self.old_price * 100))
        return 0 

    @property
    def total_ratings_count(self):
        """Возвращает общее количество оценок для продукта."""
        # self.ratings - это backref из модели Rating
        # Необходимо импортировать Rating или использовать select для подсчета, если Ratings много
        # Для простоты пока будем полагаться на то, что self.ratings доступно и не слишком велико
        # Однако, правильнее было бы сделать запрос к БД, если Ratings может быть много.
        # from .rating import Rating # Потенциальный циклический импорт, если Product импортируется в Rating
        # return Rating.query.with_entities(db.func.count(Rating.id)).filter_by(product_id=self.id).scalar() or 0
        return len(self.ratings) 

    @property
    def avg_rating(self):
        """Вычисляет средний рейтинг продукта."""
        if not self.ratings:
            return 0.0 # Возвращаем float для единообразия
        # Аналогично total_ratings_count, для больших наборов данных лучше делать агрегацию в БД
        # from .rating import Rating
        # avg_r = Rating.query.with_entities(db.func.avg(Rating.rating)).filter_by(product_id=self.id).scalar()
        # return float(avg_r) if avg_r is not None else 0.0
        return float(sum(r.rating for r in self.ratings)) / len(self.ratings)

    def __repr__(self):
        return f'<Product {self.name}>' 