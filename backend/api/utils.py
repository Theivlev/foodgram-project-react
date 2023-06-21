from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def shopping_post(request, pk, model, serializer):
    """Добавляем рецепт в список покупок"""
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(
           {'massage': 'Рецепт уже есть в списке покупок'},
           status=status.HTTP_400_BAD_REQUEST)
    model.objects.get_or_create(user=request.user, recipe=recipe)
    data = serializer(recipe).data
    return Response(data, status=status.HTTP_201_CREATED)


def shopping_delete(request, pk, model):
    """Удаляем рецепт из списка покупко"""
    recipe = get_object_or_404(Recipe, pk=pk)
    if model.objects.filter(user=request.user, recipe=recipe).exists():
        follow = get_object_or_404(model, user=request.user, recipe=recipe)
        follow.delete()
        return Response(
            {'massage': 'Рецепт успешно удален из списка покупок'},
            status=status.HTTP_204_NO_CONTENT)
    return Response({'message':  'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)


def subscrib_post(request, id, model, model_user, serializer):
    """Создает новую подписку"""

    user = request.user
    author = get_object_or_404(model_user, id=id)

    if model.objects.filter(user=user, following=author).exists():
        return Response(
            {'errors': 'Нельзя подписаться дважды'},
            status=status.HTTP_400_BAD_REQUEST)
    if user == author:
        return Response(
            {'errors': 'Нельзя подписаться на самого себя'},
            status=status.HTTP_400_BAD_REQUEST)

    follow = model.objects.create(user=user, following=author)
    serializer = serializer(follow, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def subscrib_delete(request, pk, model, model_user):
    """Удаляет существующую подписку"""

    user = request.user
    author = get_object_or_404(model_user, id=pk)

    if not model.objects.filter(user=user, following=author).exists():
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST)

    follow = get_object_or_404(model, user=user, following=author)
    follow.delete()
    return Response(
        {'message': 'Подписка удалена'},
        status=status.HTTP_204_NO_CONTENT
    )
