from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import User

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254


def validate_username_not_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            "Использовать 'me' в качестве username запрещено."
        )


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

    def validate_username(self, value):
        validate_username_not_me(value)
        return value


class MeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(UnicodeUsernameValidator(), validate_username_not_me),
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    def validate(self, data):
        username = data['username']
        email = data['email']
        if User.objects.filter(
                username=username).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже есть.'}
            )
        if User.objects.filter(
                email=email).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с такой почтой уже есть.'}
            )
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
