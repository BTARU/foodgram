"""Foodgram user models."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend.constants import (TRUNCATE_AMOUNT, USER_EMAIL_LENGTH,
                                        USER_NAME_LENGTH)


class CustomUser(AbstractUser):
    """Foodgram user model."""

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to='user_avatars',
        default=None,
        verbose_name='Avatar image'
    )
    email = models.EmailField(
        verbose_name='Email adress',
        max_length=USER_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='First name',
        max_length=USER_NAME_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Last name',
        max_length=USER_NAME_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.first_name[:TRUNCATE_AMOUNT]


class Subscription(models.Model):
    """User to user subscription relational model."""

    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribe_target = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self) -> str:
        return (
            self.subscriber.email[:TRUNCATE_AMOUNT] + ' '
            + self.subscribe_target.email[:TRUNCATE_AMOUNT]
        )
