from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.permissions import IsAdminOrAuthor
from recipes.models import (
    Ingredient,
    Recipe,
    ShoppingList,
    Tag
    )
from users.serializers import (
    RecipeFollowSerializer,
    )
from .serializers import (
    IngredientSerializer,
    RecipeChangeSerializer,
    RecipeSerializer,
    TagSerializer,
    )
from .service import generate_shopping_list
from .utils import shopping_delete, shopping_post
from api.filters import RecipeFilter


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
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

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
        serializer = RecipeFollowSerializer(
            recipe, context={'request': request})

        if request.method == 'POST':
            serializer.add_favorite_user(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            serializer.remove_favorite_user(user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request,  pk=None):
        """Добавление/удаление рецепта из списка покупок для пользователя."""
        if request.method == 'POST':
            return shopping_post(request, pk, ShoppingList,
                                 RecipeFollowSerializer)
        return shopping_delete(request, pk, ShoppingList)

    @action(
        methods=['get'], detail=False,
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок пользователя в виде текстового файла."""

        user = self.request.user
        content = generate_shopping_list(user)
        filename = "foodgram_shoping_cart.txt"
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
