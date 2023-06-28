from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Follow, UserFoodGram
from recipes.models import Recipe, Favorite
from djoser.serializers import UserCreateSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        return Follow.objects.filter(
            user=self.context['request'].user,
            following=obj
        ).exists()

    class Meta:
        model = UserFoodGram
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для получение информации о рецепте."""

    def is_favorite_user(self, user):
        return Favorite.objects.filter(
            user=user, recipe=self.instance).exists()

    def add_favorite_user(self, user):
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=self.instance)
        if not created:
            raise serializers.ValidationError('Рецепт уже в избранном')

    def remove_favorite_user(self, user):
        favorite = Favorite.objects.filter(user=user, recipe=self.instance)
        if favorite:
            favorite.delete()
        else:
            raise serializers.ValidationError('Рецепта нет в избранном')

    def validate(self, data):
        user = self.context['request'].user
        if self.context['request'].method == 'POST' and \
                self.is_favorite_user(user):
            raise serializers.ValidationError('Рецепт уже в избранном')
        if self.context['request'].method == 'DELETE' and \
                not self.is_favorite_user(user):
            raise serializers.ValidationError('Рецепта нет в избранном')
        return data

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.ReadOnlyField(source='following.recipes.count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user,
            following=obj.following
        ).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.following)
        serializer = RecipeFollowSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')


class CustomUserCreateSerializer(UserCreateSerializer):

    username = serializers.CharField()
    email = serializers.EmailField()

    def validate_username(self, value):
        """
        Проверяет, что имя пользователя уникально и не равно 'me'.
        """
        if UserFoodGram.objects.filter(username__iexact=value
                                       ).exists():
            raise ValidationError('Имя пользователя уже используется.')
        if value.casefold() == 'me':
            raise ValidationError('Имя пользователя не может быть "me".')
        return value

    def validate_email(self, value):
        """
        Проверяет, что электронная почта уникальна.
        """

        if UserFoodGram.objects.filter(email__iexact=value
                                       ).exists():
            raise ValidationError(
                'Этот адрес электронной почты уже используется.')
        return value

    class Meta(UserCreateSerializer.Meta):
        model = UserFoodGram
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password')
