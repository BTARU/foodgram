from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(
        null=True,
        upload_to='user_avatars',
        default=None
    )
    email = models.EmailField(
        'Email adress',
        max_length=254,
        unique=True
    )
    first_name = models.CharField('First name', max_length=150)
    last_name = models.CharField('Last name', max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
