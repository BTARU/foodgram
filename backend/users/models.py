from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

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
