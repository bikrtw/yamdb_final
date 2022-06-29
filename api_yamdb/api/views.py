from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews import models
from reviews.models import Review
from . import serializers, filters
from .permission import IsAdmin, IsAdminOrReadOnly, ReviewCommentPermission


class BaseCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class CreateListDestroy(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class GenreViewSet(CreateListDestroy):
    queryset = models.Genre.objects.all().order_by('-id')
    serializer_class = serializers.GenreSerializer
    permission_classes = [IsAdminOrReadOnly]

    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateListDestroy):
    queryset = models.Category.objects.all().order_by('-id')
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = models.Title.objects.all().order_by('-id').annotate(
        mean_score=Avg('reviews__score')
    )
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.TitleDisplaySerializer
        return serializers.TitleCreateUpdateSerializer


class GetTokenApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(models.User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return models.User.objects.all()

    @action(detail=False, methods=['GET', 'PATCH'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def get_or_update_user(self, request):
        username = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(username)
            return Response(serializer.data)

        # Patch
        serializer = self.get_serializer(username, data=request.data,
                                         partial=True)

        if serializer.is_valid() and self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(role=username.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all().order_by('-id')
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = models.User.objects.get_or_create(
                username=username,
                email=email)
        except IntegrityError:
            """Если существует пользователь с таким же email, но другим
            username или таким же username и другим email. В этом случае
            get_or_create не спасет. Возвращаем ошибку."""
            return Response(status=status.HTTP_400_BAD_REQUEST)
        message = default_token_generator.make_token(user)
        email = EmailMessage(
            message,
            to=[serializer.validated_data.get('email')]
        )
        email.send()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [ReviewCommentPermission]

    def get_queryset(self):
        title = get_object_or_404(models.Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        title = get_object_or_404(models.Title, pk=self.kwargs.get('title_id'))
        author = self.request.user
        if Review.objects.filter(author=author, title=title).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        title = get_object_or_404(models.Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [ReviewCommentPermission]

    def get_queryset(self):
        review = get_object_or_404(
            models.Review,
            pk=self.kwargs.get('review_id')
        )
        # Проверяем, соответствует ли отзыв произведению.
        if review.title.id != int(self.kwargs.get('title_id')):
            raise Http404('Отзыв относится к другому произведению.')
        return review.comments.all().order_by('-id')

    def perform_create(self, serializer):
        review = get_object_or_404(
            models.Review,
            pk=self.kwargs.get('review_id')
        )
        # Проверяем, соответствует ли отзыв произведению.
        if review.title.id != int(self.kwargs.get('title_id')):
            raise Http404('Отзыв относится к другому произведению.')
        serializer.save(author=self.request.user, review=review)
