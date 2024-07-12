from django.db import models

from foodgram_backend.constants import (INGREDIENT_M_UNIT_LENGTH,
                                        INGREDIENT_NAME_LENGTH,
                                        TRUNCATE_AMOUNT)


class Ingredient(models.Model):
    """Ингредиент для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_M_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]
