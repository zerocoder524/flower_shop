from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """Букет или другой товар цветочного магазина."""

    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )

    description = models.TextField(
        verbose_name="Описание",
        blank=True,
    )

    price = models.DecimalField(
        verbose_name="Цена",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01"),
                message="Цена должна быть больше нуля.",
            )
        ],
    )

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="products/",
        blank=True,
    )

    is_available = models.BooleanField(
        verbose_name="Доступен для заказа",
        default=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="catalog_product_price_gt_0",
            ),
        ]

    def __str__(self) -> str:
        return self.name