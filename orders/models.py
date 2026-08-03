from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Order(models.Model):
    """Заказ на доставку цветов."""

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        ACCEPTED = "accepted", "Принят"
        IN_PROGRESS = "in_progress", "В работе"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="Товар",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        default=1,
        validators=[
            MinValueValidator(
                1,
                message="Количество должно быть не меньше одного.",
            )
        ],
    )

    customer_name = models.CharField(
        verbose_name="Имя заказчика",
        max_length=150,
    )

    phone = models.CharField(
        verbose_name="Телефон",
        max_length=30,
    )

    recipient_name = models.CharField(
        verbose_name="Имя получателя",
        max_length=150,
        blank=True,
    )

    delivery_address = models.TextField(
        verbose_name="Адрес доставки",
    )

    delivery_date = models.DateField(
        verbose_name="Дата доставки",
    )

    delivery_time = models.TimeField(
        verbose_name="Время доставки",
    )

    comment = models.TextField(
        verbose_name="Комментарий",
        blank=True,
    )

    unit_price = models.DecimalField(
        verbose_name="Цена за единицу",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    total_price = models.DecimalField(
        verbose_name="Итоговая стоимость",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="orders_order_quantity_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="orders_order_unit_price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name="orders_order_total_price_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"Заказ №{self.pk}" if self.pk else "Новый заказ"

    def clean(self) -> None:
        """Проверяет дату доставки при создании заказа."""

        super().clean()

        if (
            self._state.adding
            and self.delivery_date
            and self.delivery_date < timezone.localdate()
        ):
            raise ValidationError(
                {
                    "delivery_date": (
                        "Дата доставки не может находиться в прошлом."
                    )
                }
            )

        if self.product_id and not self.product.is_available:
            raise ValidationError(
                {
                    "product": "Этот товар сейчас недоступен для заказа."
                }
            )

    def save(self, *args, **kwargs) -> None:
        """
        Сохраняет цену товара на момент создания заказа
        и рассчитывает итоговую стоимость.
        """

        if self._state.adding:
            self.unit_price = self.product.price

        self.total_price = self.unit_price * self.quantity

        update_fields = kwargs.get("update_fields")

        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {
                "unit_price",
                "total_price",
            }

        super().save(*args, **kwargs)