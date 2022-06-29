from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('genres', views.GenreViewSet)
router.register('categories', views.CategoryViewSet)
router.register('titles', views.TitleViewSet)
router.register('auth/email', views.CreateUserViewSet)
router.register('users', views.UserViewSet)
router.register('auth/signup', views.CreateUserViewSet)
router.register('titles', views.TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/token/', views.GetTokenApiView.as_view(),
        name='token_obtain_pair'),
]
