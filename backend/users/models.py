from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
# from django.core.exceptions import ValidationError

from foodgram_backend.constants import (TRUNCATE_AMOUNT, USER_EMAIL_LENGTH,
                                        USER_NAME_LENGTH)
from .validators import validate_username


class CustomUser(AbstractUser):
    """Основная модель пользователя."""

    username = models.CharField(
        verbose_name='Юзернейм пользователя',
        max_length=USER_NAME_LENGTH,
        unique=True,
        help_text=(
            'Уникальный юзернейм. '
            'Разрешены только буквы, цифры и символы @/./+/-/_'
        ),
        validators=[validate_username, UnicodeUsernameValidator()],
    )
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to='user_avatars',
        default=None,
        verbose_name='Фото пользователя'
    )
    email = models.EmailField(
        verbose_name='Email адрес',
        max_length=USER_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USER_NAME_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=USER_NAME_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.first_name[:TRUNCATE_AMOUNT]


# class Subscription(models.Model):
#     """Связующая модель подписок пользователей друг на друга."""

#     subscriber = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='subscriptions',
#         verbose_name='Подписчик'
#     )
#     subscribe_target = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='followers',
#         verbose_name='На кого подписан'
#     )

#     class Meta:
#         verbose_name = 'Подписка'
#         verbose_name_plural = 'Подписки'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('subscriber', 'subscribe_target'),
#                 name='unique_user_subscribe',
#             ),
#         ]

#     def __str__(self) -> str:
#         return (
#             self.subscriber.email[:TRUNCATE_AMOUNT] + ' '
#             + self.subscribe_target.email[:TRUNCATE_AMOUNT]
#         )

#     def clean(self) -> None:
#         if self.subscriber == self.subscribe_target:
#             raise ValidationError(
#                 {
#                     'subscribe_target': 'Нельзя подписаться на себя.'
#                 }
#             )
