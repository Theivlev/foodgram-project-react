from recipes.models import Recipe, RecipeIngredient, ShoppingList
from django.core.files.base import ContentFile
import base64
from rest_framework import serializers


def generate_shopping_list(user):
    shopping_list = ShoppingList.objects.filter(user=user)
    recipe_id = shopping_list.values_list('recipe', flat=True)
    recipes = Recipe.objects.filter(id__in=recipe_id)
    shopping_list_data = {}
    for recipe in recipes:
        for ingredient in recipe.ingredients.all():
            recipe_ingredient = RecipeIngredient.objects.filter(
                recipe=recipe, ingredient=ingredient).first()
            amount = (recipe_ingredient.amount *
                      recipe.ingredients.count())
            if ingredient.name in shopping_list_data:
                shopping_list_data[ingredient.name] += amount
            else:
                shopping_list_data[ingredient.name] = amount

        shopping_list_string = ''
        for name, amount in shopping_list_data.items():
            shopping_list_string += f'{name}: {amount}\n'

    return shopping_list_string


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
