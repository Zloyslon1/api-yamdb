from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (
    CONFIRMATION_CODE_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    MAX_SCORE,
    MIN_SCORE,
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    TEXT_PREVIEW_LENGTH,
    USERNAME_MAX_LENGTH,
    current_year,
)
from reviews.validators import validate_username


def current_year():
    """Текущий год — верхняя граница года выпуска произведения."""
    return date.today().year


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    bio = models.TextField(
        'О себе',
        blank=True,
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class NameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    slug = models.SlugField('Слаг', max_length=SLUG_MAX_LENGTH, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(NameSlugModel):
    """Модель категории произведения.

    Каждое произведение относится ровно к одной категории.
    """

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Модель жанра произведения.

    Произведение может относиться к нескольким жанрам.
    """

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения (фильмы, книги, музыка и т.д.).

    Произведение относится к одной категории и может иметь
    несколько жанров. Рейтинг вычисляется на лету аннотацией
    среднего отзывов через reviews__score.
    """

    name = models.CharField(
        'Название',
        max_length=NAME_MAX_LENGTH,
    )
    year = models.IntegerField(
        'Год выпуска',
        validators=(
            MaxValueValidator(current_year),
        ),
    )
    description = models.TextField(
        'Описание',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name


class BaseReviewComment(models.Model):
    """Абстрактная база с автором, текстом и датой публикации."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(model_name)ss'

    def __str__(self):
        return self.text[:TEXT_PREVIEW_LENGTH]


class Review(BaseReviewComment):
    """Отзыв пользователя на произведение с оценкой."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE),
        ),
    )

    class Meta(BaseReviewComment.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_per_author',
            ),
        )


class Comment(BaseReviewComment):
    """Комментарий к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(BaseReviewComment.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
