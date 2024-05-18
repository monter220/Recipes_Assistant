from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db import models

from core.validators import validate_username, validate_field_text


class FoodgramUser(AbstractUser):
    REQUIRED_FIELDS: list[str] = ['username', 'first_name', 'last_name', ]
    USERNAME_FIELD: str = 'email'

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USER_MAX_LENGTH_FIELD,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username, ],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.USER_MAX_LENGTH_FIELD,
        validators=[validate_field_text, ],
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.USER_MAX_LENGTH_FIELD,
        validators=[validate_field_text, ],
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribe_author',
    )
    subscriber = models.ForeignKey(
        FoodgramUser,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name="\nПодписаться на себя? Серьезно? так нельзя\n"
            ),
        ]

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
