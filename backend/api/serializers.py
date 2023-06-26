from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag)
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
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
            'cooking_time'
            )


class RecipeChangeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепте."""

    id = serializers.IntegerField()
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'recipe', 'amount',)


class RecipeChangeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeChangeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField()

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
                ))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            recipe_ingredients = []
            for ingredient in ingredients:
                recipe_ingredients.append(RecipeIngredient(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient,
                                                 pk=ingredient['id']),
                    amount=ingredient['amount']
                ))
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance

    def validate(self, data):
        if len(data['tags']) == 0:
            raise serializers.ValidationError('Укажите хотя бы один тег.')

        if len(set(data['tags'])) != len(data['tags']):
            raise serializers.ValidationError('Теги не должны повторяться.')

        if data.get('cooking_time', 0) < 1:
            raise serializers.ValidationError(
                'Минимальное время приготовления 1 минута.')

        if len(data['ingredients']) < 1:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент.')
        ingredients_id = set()
        for ingredient in data['ingredients']:
            if ingredient['id'] in ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredients_id.add(ingredient['id'])

        return data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализтор для списка избранного."""
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe',)


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализтор для списка покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
