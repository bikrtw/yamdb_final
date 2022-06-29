from datetime import date

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Avg


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    SADMIN = 'sadmin'
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
        (SADMIN, 'sadmin'),
    )

    bio = models.TextField(max_length=500, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLES, default='user')
    confirmation_code = models.CharField(max_length=200, default='FOOBAR')
    email = models.EmailField(unique=True)

    class Meta(AbstractUser.Meta):
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.is_superuser or self.role == User.ADMIN

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(
        db_index=True,
        validators=[MaxValueValidator(date.today().year)])
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='GenreTitle',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
    )

    @property
    def average_score(self):
        if hasattr(self, 'mean_score'):
            return self.mean_score
        return self.reviews.aggregate(Avg('score'))


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_genre_title',
                fields=['genre', 'title'],
            ),
        ]


class Review(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_review',
                fields=['author', 'title'],
            ),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
