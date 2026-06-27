import string
from datetime import date

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
CONFIRMATION_CODE_MAX_LENGTH = 255
CONFIRMATION_CODE_LENGTH = 6
CONFIRMATION_CODE_ALPHABET = string.digits
ME_URL_PATH = 'me'
MIN_SCORE = 1
MAX_SCORE = 10
TEXT_PREVIEW_LENGTH = 50

SLUG_MAX_LENGTH = 50
NAME_MAX_LENGTH = 256


def current_year():
    """Текущий год для ограничения поля year."""
    return date.today().year
