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


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        required=True,
    )


class NameSlugSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для моделей с name и slug."""

    class Meta:
        fields = ('name', 'slug')


class CategorySerializer(NameSlugSerializer):
    """Сериализатор категории."""

    class Meta(NameSlugSerializer.Meta):
        model = Category


class GenreSerializer(NameSlugSerializer):
    """Сериализатор жанра."""

    class Meta(NameSlugSerializer.Meta):
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведения.

    Принимает category и genre по slug.
    Возвращает вложенные объекты категории и жанров,
    а также аннотированный рейтинг.
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
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = (
            CategorySerializer(instance.category).data
            if instance.category else None
        )
        rep['genre'] = GenreSerializer(
            instance.genre.all(), many=True
        ).data
        return rep


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
            title = Title.objects.get(pk=title_id)
            raise serializers.ValidationError(
                f'{request.user.username} уже оставил отзыв '
                f'на произведение «{title.name}».'
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
