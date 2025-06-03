"""
Расширения Flask для приложения
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2 import nodes
from jinja2.ext import Extension

# Инициализация расширений без привязки к приложению
db = SQLAlchemy()
migrate = Migrate()

# Расширение для добавления команды break в Jinja2
class BreakExtension(Extension):
    tags = {'break'}

    def parse(self, parser):
        token = next(parser.stream)
        return nodes.CallBlock(
            self.call_method('_break', []),
            [], [], []
        ).set_lineno(token.lineno)

    def _break(self, caller):
        return '' 