from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import IsAdmin
from api.serializers import (
    GetTokenSerializer,
    MeSerializer,
    SignUpSerializer,
    UserSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
)
from reviews.constants import (
    CONFIRMATION_CODE_ALPHABET,
    CONFIRMATION_CODE_LENGTH,
    ME_URL_PATH,
)
from reviews.models import Category, Genre, Review, Title, User

EMAIL_SUBJECT = 'Код подтверждения YaMDb'


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей (только для админа)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w.@+-]+'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    @action(
        detail=False,
        methods=('get', 'patch'),
        url_path=ME_URL_PATH,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)
        serializer = MeSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except IntegrityError:
        errors = {}
        for existing in User.objects.filter(
                Q(username=username) | Q(email=email)):
            if existing.username == username:
                errors['username'] = 'Этот username уже занят.'
            if existing.email == email:
                errors['email'] = 'Эта почта уже занята.'
        raise ValidationError(errors)
    user.confirmation_code = get_random_string(
        CONFIRMATION_CODE_LENGTH, CONFIRMATION_CODE_ALPHABET
    )
    user.save(update_fields=('confirmation_code',))
    send_mail(
        subject=EMAIL_SUBJECT,
        message=f'Ваш код подтверждения: {user.confirmation_code}',
        from_email=None,
        recipient_list=(user.email,),
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((AllowAny,))
def token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    code = serializer.validated_data['confirmation_code']
    if not user.confirmation_code or user.confirmation_code != code:
        user.confirmation_code = ''
        user.save(update_fields=('confirmation_code',))
        raise ValidationError('Неверный код подтверждения. Запросите новый.')
    user.confirmation_code = ''
    user.save(update_fields=('confirmation_code',))
    return Response(
        {'token': str(AccessToken.for_user(user))},
        status=status.HTTP_200_OK,
    )


class NameSlugViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Базовый ViewSet для моделей с name и slug.

    Поиск по name. Идентификация по slug.
    """

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(NameSlugViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(NameSlugViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений (read-write)."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).distinct()
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet отзывов к произведению (вложен в /titles/)."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet комментариев к отзыву (вложен в /reviews/)."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
