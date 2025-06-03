"""
Blueprint для обработки форм обратной связи
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from my_app.extensions import db
from my_app.models import FeedbackMessage
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Создаем Blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('/submit', methods=['POST'])
def submit():
    """Обработка формы обратной связи"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        message_text = request.form.get('message')

        # Получаем email получателя (администратора)
        recipient_email = request.form.get('recipient_email')

        # Если email получателя не указан в форме, используем значение из конфигурации
        if not recipient_email:
            recipient_email = current_app.config.get('MAIL_DEFAULT_RECEIVER', 'qqdslk@gmail.com')

        # Создаем тему сообщения
        subject = f"Новое сообщение от {name} - Форма обратной связи"

        # Формируем сообщение для записи в базу данных
        feedback = FeedbackMessage(
            name=name,
            email=email,
            subject=subject,
            message=f"Телефон: {phone}\n\n{message_text}"
        )

        try:
            # Сохраняем сообщение в базу данных
            db.session.add(feedback)
            db.session.commit()
            current_app.logger.info(f"Сообщение сохранено в базе данных (ID: {feedback.id})")

            # Отправляем email
            email_sent = send_email(recipient_email, subject, name, email, phone, message_text)

            # Уведомляем пользователя об успешной отправке
            if email_sent:
                flash('Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.', 'success')
                current_app.logger.info(f"Email успешно отправлен на адрес {recipient_email}")
            else:
                flash('Ваше сообщение сохранено. Наши сотрудники обработают его в ближайшее время.', 'success')
                current_app.logger.warning("Email не был отправлен, но сообщение сохранено в базе данных")
        except Exception as e:
            # Логируем ошибку
            current_app.logger.error(f"Ошибка при отправке сообщения: {str(e)}")
            flash('Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.', 'error')
            db.session.rollback()

    # Перенаправляем на страницу контактов
    return redirect(url_for('static_pages.contact'))


def send_email(recipient, subject, name, sender_email, phone, message_text):
    """Отправляет электронное письмо с данными формы обратной связи"""
    try:
        # Формируем текст письма
        email_content = f"""
        Новое сообщение с формы обратной связи!

        Имя: {name}
        Email: {sender_email}
        Телефон: {phone}

        Сообщение:
        {message_text}

        Дата отправки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """

        # Получаем настройки SMTP
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT')
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        mail_default_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username if mail_username else 'noreply@example.com')

        # Если настройки SMTP отсутствуют, только логируем сообщение
        if not all([mail_server, mail_port, mail_username, mail_password]):
            current_app.logger.warning(
                f"SMTP не настроен. Сообщение сохранено в базе данных, но email не отправлен.\n"
                f"Получатель: {recipient}\n"
                f"От: {name} ({sender_email})\n"
                f"Сообщение: {message_text[:100]}..."
            )
            return False

        # Создаем объект сообщения
        msg = EmailMessage()
        msg.set_content(email_content)

        # Указываем заголовки
        msg['Subject'] = subject
        msg['From'] = mail_default_sender
        msg['To'] = recipient
        # Добавляем Reply-To, чтобы ответы шли отправителю формы
        msg['Reply-To'] = sender_email

        # Подробное логирование для отладки
        current_app.logger.info(f"Попытка отправки email через SMTP сервер: {mail_server}:{mail_port}")

        # Отправляем сообщение
        with smtplib.SMTP(mail_server, int(mail_port)) as server:
            # Включаем подробное логирование SMTP (в режиме разработки)
            if current_app.debug:
                server.set_debuglevel(1)

            # Используем TLS если настроено
            if mail_use_tls:
                server.starttls()
                current_app.logger.info("TLS соединение установлено")

            # Авторизация
            current_app.logger.info(f"Авторизация пользователя: {mail_username}")
            server.login(mail_username, mail_password)

            # Отправка сообщения
            server.send_message(msg)
            current_app.logger.info(f"Сообщение успешно отправлено получателю: {recipient}")

        return True
    except Exception as e:
        current_app.logger.error(f"Ошибка отправки email: {str(e)}")
        return False