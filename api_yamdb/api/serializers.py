from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ('name', 'slug')


class TitleDisplaySerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'category',
                  'genre')
        required_fields = ('name', 'year', 'category', 'genre')

    def get_rating(self, obj):
        return round(obj.average_score, 1) if obj.average_score else None


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=models.Category.objects.all())
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=models.Genre.objects.all(), many=True)

    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'category',
                  'genre')
        required_fields = ('name', 'year', 'category', 'genre')

    def get_rating(self, obj):
        """Сделано в соответствии с документацией.

        При отсутствии обзоров необходимо чтобы возвращалось значение None,
        в т.ч. при создании Title в ответе должно быть поле рейтинга.
        """
        return


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = models.Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author',)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    bio = serializers.CharField()

    class Meta:
        model = models.User
        fields = (
            'bio', 'first_name', 'last_name',
            'username', 'email', 'role'
        )
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=models.User.objects.all())]
    )

    class Meta:
        model = models.User
        fields = (
            'first_name', 'last_name',
            'username', 'bio', 'email', 'role'
        )


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя создать пользователя с username = "me"')
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = models.Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
