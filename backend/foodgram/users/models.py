from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
