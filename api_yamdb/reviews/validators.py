from datetime import date

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from reviews.constants import FORBIDDEN_USERNAME

validate_username_pattern = UnicodeUsernameValidator()


def validate_username(username):
    """Проверка username: запрет имени-заглушки и паттерн из ТЗ."""
    if username == FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Имя {FORBIDDEN_USERNAME} использовать как username нельзя.'
        )
    validate_username_pattern(username)


def current_year():
    """Текущий год для ограничения поля year."""
    return date.today().year
