from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return ShoppingList.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        ingredient = RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredient, many=True)
        return serializer.data

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'title', 'image',
            'description', 'ingredients',
            'tags', 'is_in_shopping_cart',
            'is_favorited',
            'cooking_time')


class RecipeChangeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепте."""

    id = serializers.IntegerField()
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    quantity = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'recipe', 'quantity')


class RecipeChangeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeChangeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for i in tags:
            recipe.tags.add(i)

        for j in ingredients:
            quantity = j['quantity']
            ingredient = get_object_or_404(Ingredient, pk=j['id'])

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity
                )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        current_tags = instance.tags.all()

        for i in current_tags:
            if i not in tags:
                instance.tags.remove(i)
        for j in tags:
            if j not in current_tags:
                instance.tags.add(j)

        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()

            for i in ingredients:
                ingredient = get_object_or_404(Ingredient, pk=i['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    quantity=i['quantity']
                )

        return instance

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'title', 'image',
            'description', 'ingredients',
            'tags', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализтор для списка избранного."""
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe',)


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализтор для списка покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')
