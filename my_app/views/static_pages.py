"""
Blueprint для статических страниц
"""
from flask import Blueprint, render_template

# Создаем Blueprint с префиксом '/pages'
static_pages_bp = Blueprint('static_pages', __name__, url_prefix='/pages')

@static_pages_bp.route('/about')
def about():
    """Страница о компании"""
    return render_template('about.html')

@static_pages_bp.route('/delivery')
def delivery():
    """Страница о доставке"""
    return render_template('delivery.html')

@static_pages_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница контактов"""
    return render_template('contact.html')

@static_pages_bp.route('/sitemap')
def sitemap():
    """Карта сайта"""
    return render_template('sitemap.html')

@static_pages_bp.route('/terms')
def terms():
    """Условия использования"""
    return render_template('terms.html')

@static_pages_bp.route('/privacy')
def privacy():
    """Политика конфиденциальности"""
    return render_template('privacy.html')

@static_pages_bp.route('/returns')
def returns():
    """Возврат товара"""
    return render_template('returns.html')

@static_pages_bp.route('/warranty')
def warranty():
    """Гарантия"""
    return render_template('warranty.html')

@static_pages_bp.route('/faq')
def faq():
    """Часто задаваемые вопросы"""
    return render_template('faq.html') 