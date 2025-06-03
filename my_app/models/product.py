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

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def discount_percent(self):
        """Вычисляет процент скидки, если есть старая цена"""
        if self.old_price and self.old_price > self.price:
            return int(100 - (self.price / self.old_price * 100))
        return 0 