from django.db import models

from foodgram_backend.constants import TRUNCATE_AMOUNT, TAG_FIELD_MAX_LENGTH


class Tag(models.Model):
    """Тэг для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_FIELD_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=TAG_FIELD_MAX_LENGTH,
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]
