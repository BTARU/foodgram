from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='user_avatars'
    )
