from rest_framework import serializers

from reviews.constants import (
    CONFIRMATION_CODE_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class MeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=(validate_username,),
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        required=True,
    )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории.

    Используется для list/create/destroy. Поля name и slug.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра.

    Используется для list/create/destroy. Поля name и slug.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для GET-запросов к произведениям.

    Возвращает вложенные объекты категории и жанров,
    а также аннотированный рейтинг.
    """

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        """Вернуть аннотированный рейтинг или None."""
        return getattr(obj, 'rating', None)


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для POST/PATCH-запросов к произведениям.

    Принимает category и genre по slug. При успехе возвращает
    полный объект, включая id.
    """

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        read_only_fields = ('id',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва. Автор подставляется автоматически."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """На POST запретить второй отзыв того же автора."""
        request = self.context['request']
        if request.method != 'POST':
            return data
        title_id = self.context['view'].kwargs['title_id']
        if Review.objects.filter(
                title_id=title_id, author=request.user).exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария. Автор подставляется автоматически."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
