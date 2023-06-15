from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow, UserFoodGram


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            following=obj
        ).exists()

    class Meta:
        model = UserFoodGram
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для получение информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')


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
            'id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')
