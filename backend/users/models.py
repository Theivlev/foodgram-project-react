from django.contrib.auth.models import AbstractUser
from django.db import models


class UserFoodGram(AbstractUser):
    """Модель пользователя сервиса FoodGram."""

    email = models.EmailField(
        max_length=254, blank=False, unique=True, verbose_name='Почта')
    username = models.CharField(
        max_length=128, unique=True, verbose_name='Никнейм')
    first_name = models.CharField(
        max_length=150, verbose_name='Имя пользователя')
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия пользователя')
    password = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Имя пользователя'
        verbose_name_plural = 'Имя пользователей'

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    """
    Модель подписки на пользователя сервиса FoodGram.

    Содержит поля для связи подписчика и автора рецепта.
    """

    user = models.ForeignKey(
        UserFoodGram,
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Подписчик на автора рецепта',
    )
    following = models.ForeignKey(
        UserFoodGram,
        related_name='followed',
        on_delete=models.CASCADE,
        help_text='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Имя пользователя'
        verbose_name_plural = 'Имя пользователей'
        constraints = [models.UniqueConstraint(
            fields=['following', 'user'],
            name='unique_object'
        )]
        ordering = ['-user']

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
