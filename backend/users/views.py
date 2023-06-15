from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination

from .models import Follow, UserFoodGram
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):
    """ViewSet для работы с пользователями сервиса FoodGram."""

    queryset = UserFoodGram.objects.all().order_by('-date_joined')
    pagination_class = CustomPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),)
    def me(self, request):
        """Выводит информацию о пользователе"""

        serializer = CustomUserSerializer(
            request.user, context={'request': request})
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user,
                data=request.data,
                context={'request': request},
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, id=None):
        """Подписывает пользователя на другого пользователя."""

        user = request.user
        author = get_object_or_404(UserFoodGram, id=id)
        if self.request.method == 'POST':
            if Follow.objects.filter(user=user, following=author).exists():
                return Response(
                    {'errors': 'Нельзя подписаться дважды'},
                    status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=user, following=author)
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        if Follow.objects.filter(user=user, following=author).exists():
            follow = get_object_or_404(Follow, user=user, following=author)
            follow.delete()
            return Response(
                {'message': 'Подписка удалена'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        """
        Возвращает список пользователей, на которых
        подписан текущий пользователь.
        """
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )

        response_data = {
            'count': len(pages),
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results': serializer.data
                         }
        return Response(response_data)
