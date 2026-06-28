from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.constants import ME_URL_PATH, VALIDATE_USERNAME_PATTERN



def validate_username(username):
    """Проверка username: запрет служебного имени и паттерн из ТЗ."""
    if username == ME_URL_PATH:
        raise ValidationError(
            f'Имя {ME_URL_PATH} использовать как username нельзя.'
        )
    VALIDATE_USERNAME_PATTERN(username)
