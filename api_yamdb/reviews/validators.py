from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from reviews.constants import FORBIDDEN_USERNAME

validate_username_pattern = UnicodeUsernameValidator()


def validate_username(value):
    """Проверка username: запрет имени-заглушки и паттерн из ТЗ."""
    if value == FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Имя {FORBIDDEN_USERNAME} использовать как username нельзя.'
        )
    validate_username_pattern(value)
