from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.constants import ME_URL_PATH

validate_username_pattern = RegexValidator(regex=r'^[\w.@+-]+\Z')


def validate_username(username):
    """Проверка username: запрет служебного имени и паттерн из ТЗ."""
    if username == ME_URL_PATH:
        raise ValidationError(
            f'Имя {ME_URL_PATH} использовать как username нельзя.'
        )
    validate_username_pattern(username)


def current_year():
    """Текущий год для ограничения поля year."""
    return date.today().year
