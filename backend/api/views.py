from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.permissions import IsAdminOrAuthor
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.serializers import RecipeFollowSerializer

from .render import PlainTextRenderer
from .serializers import (IngredientSerializer, RecipeChangeSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet для объектов Ingredient, обеспечивает создание, чтение,
    обновление и удаление объектов,
    а также поиск по полю "name".
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name', 'name')


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet для объектов Tag, обеспечивает создание, чтение, обновление
    и удаление объектов.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для объектов Recipe, обеспечивает создание, чтение,
    обновление и удаление объектов,
    при условии, что пользователь аутентифицирован.
    Класс также определяет класс пагинации CustomPagination и
    методы обработки запросов HTTP (get, post, patch, delete).
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    renderer_classes = [JSONRenderer, PlainTextRenderer]
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeChangeSerializer
        return RecipeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'massage': 'Рецепт успешно удален'},
            status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],)
    def favorite(self, request,  pk=None):
        """Добавление/удаление рецепта из списка избранных для пользователя."""

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'message': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeFollowSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'message': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request,  pk=None):
        """Добавление/удаление рецепта из списка покупок для пользователя."""

        user = request.user
        recipe = get_object_or_404(Recipe,  pk=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                return Response(
                    {'message':  'Рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingList.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = ShoppingListSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not ShoppingList.objects.filter(user=user,
                                               recipe=recipe).exists():
                return Response(
                    {'message':  'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)
            shopping_list = get_object_or_404(
                ShoppingList,
                user=user,
                recipe=recipe)
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок пользователя в виде текстового файла."""

        user = self.request.user
        shopping_list = ShoppingList.objects.filter(user=user)
        recipe_id = shopping_list.values_list('recipe', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_id)
        shopping_list_data = {}
        for i in recipes:
            for j in i.ingredients.all():
                recipe_ingredient = RecipeIngredient.objects.filter(
                    recipe=i, ingredient=j).first()
                quantity = recipe_ingredient.quantity * i.ingredients.count()
                if j.name in shopping_list_data:
                    shopping_list_data[j.name] += quantity
                else:
                    shopping_list_data[j.name] = quantity
        shopping_list_string = ''
        for name, quantity in shopping_list_data.items():
            shopping_list_string += f'{name}: {quantity}\n'

        filename = "foodgram_shoping_cart.txt"
        response = HttpResponse(
            shopping_list_string, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
