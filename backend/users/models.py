from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        null=True,
        upload_to='user_avatars',
        default=None,
        verbose_name='Avatar image'
    )
    email = models.EmailField(
        verbose_name='Email adress',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='First name',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Last name',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
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
