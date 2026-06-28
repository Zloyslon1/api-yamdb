from django.core.exceptions import ValidationError

from reviews.constants import RESERVED_USERNAMES, VALIDATE_USERNAME_PATTERN


def validate_username(username):
    """Проверка username: запрет служебных имён и паттерн из ТЗ."""
    if username in RESERVED_USERNAMES:
        raise ValidationError(
            f'Имя {username} использовать как username нельзя.'
        )
    VALIDATE_USERNAME_PATTERN(username)
    return username
