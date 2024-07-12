from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from foodgram_backend.constants import TRUNCATE_AMOUNT

User = get_user_model()


class Subscription(models.Model):
    """Связующая модель подписок пользователей друг на друга."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    subscribe_target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='На кого подписан'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'subscribe_target'),
                name='unique_user_subscribe',
            ),
        ]

    def __str__(self) -> str:
        return (
            self.subscriber.email[:TRUNCATE_AMOUNT] + ' '
            + self.subscribe_target.email[:TRUNCATE_AMOUNT]
        )

    def clean(self) -> None:
        if self.subscriber == self.subscribe_target:
            raise ValidationError(
                {
                    'subscribe_target': 'Нельзя подписаться на себя.'
                }
            )
