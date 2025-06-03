"""
Представления (маршруты) приложения
"""

# Импорт представлений для регистрации
from .shop import shop_bp
from .admin import admin_bp
from .auth import auth_bp
from .cart import cart_bp
from .profile import profile_bp
from .static_pages import static_pages_bp
from .favorites import favorites_bp
from .compare import compare_bp
from .feedback import feedback_bp
from .reviews import reviews_bp

# Список всех blueprint для регистрации
all_blueprints = [
    shop_bp,
    admin_bp,
    auth_bp,
    cart_bp,
    profile_bp,
    static_pages_bp,
    favorites_bp,
    compare_bp,
    feedback_bp,
    reviews_bp
] 