from flask import Blueprint, render_template

news_bp = Blueprint('news', __name__, url_prefix='/news')

# Временные данные для новостей
sample_news = [
    {
        'id': 1,
        'title': 'Открытие нового сезона!',
        'date': '2024-08-01',
        'short_description': 'Мы рады объявить о начале нового сезона с множеством новинок и скидок.',
        'content': 'Полное описание новости о новом сезоне... Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.'
    },
    {
        'id': 2,
        'title': 'Большая летняя распродажа',
        'date': '2024-07-15',
        'short_description': 'Не пропустите нашу грандиозную летнюю распродажу со скидками до 70%!',
        'content': 'Подробности о летней распродаже... Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur tortor. Pellentesque nibh. Aenean quam. In scelerisque sem at dolor. Maecenas mattis. Sed convallis tristique sem. Proin ut ligula vel nunc egestas porttitor. Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa. Fusce ac turpis quis ligula lacinia aliquet. Mauris ipsum. Nulla metus metus, ullamcorper vel, tincidunt sed, euismod in, nibh.'
    },
    {
        'id': 3,
        'title': 'Новые поступления электроники',
        'date': '2024-07-05',
        'short_description': 'Ознакомьтесь с последними новинками в категории электроники.',
        'content': 'Обзор новых гаджетов и устройств... Quisque volutpat condimentum velit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam nec ante. Sed lacinia, urna non tincidunt mattis, tortor neque adipiscing diam, a cursus ipsum ante quis turpis. Nulla facilisi. Ut fringilla. Suspendisse potenti. Nunc feugiat mi a tellus consequat imperdiet. Vestibulum sapien. Proin quam. Etiam ultrices. Suspendisse in justo eu magna luctus suscipit.'
    }
]

@news_bp.route('/')
def news_list():
    """Отображает список всех новостей."""
    return render_template('news_list.html', news_items=sample_news, title="Новости")

@news_bp.route('/<int:news_id>')
def news_detail(news_id):
    """Отображает детальную страницу новости."""
    news_item = next((item for item in sample_news if item['id'] == news_id), None)
    if news_item:
        return render_template('news_detail.html', news_item=news_item, title=news_item['title'])
    return "Новость не найдена", 404 