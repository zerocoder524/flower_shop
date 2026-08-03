import re
from datetime import datetime

from django import forms
from django.utils import timezone

from .models import Order


PHONE_PATTERN = re.compile(
    r"^\+?[0-9\s()\-]{7,20}$"
)


class OrderForm(forms.ModelForm):
    """Пользовательская форма оформления заказа."""

    class Meta:
        model = Order

        fields = (
            "quantity",
            "customer_name",
            "phone",
            "recipient_name",
            "delivery_address",
            "delivery_date",
            "delivery_time",
            "comment",
        )

        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "min": 1,
                }
            ),
            "delivery_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "delivery_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
            "delivery_address": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(
        self,
        *args,
        product=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.product = product

        self.fields["delivery_date"].widget.attrs[
            "min"
        ] = timezone.localdate().isoformat()

    def clean_phone(self) -> str:
        phone = self.cleaned_data["phone"].strip()

        if not PHONE_PATTERN.fullmatch(phone):
            raise forms.ValidationError(
                "Введите корректный номер телефона."
            )

        return phone

    def clean(self):
        cleaned_data = super().clean()

        if self.product is None:
            raise forms.ValidationError(
                "Товар не выбран."
            )

        if not self.product.is_available:
            raise forms.ValidationError(
                "Выбранный товар больше недоступен."
            )

        delivery_date = cleaned_data.get(
            "delivery_date"
        )
        delivery_time = cleaned_data.get(
            "delivery_time"
        )

        if delivery_date and delivery_time:
            delivery_datetime = timezone.make_aware(
                datetime.combine(
                    delivery_date,
                    delivery_time,
                ),
                timezone=timezone.get_current_timezone(),
            )

            if delivery_datetime <= timezone.now():
                self.add_error(
                    "delivery_time",
                    "Дата и время доставки должны быть в будущем.",
                )

        return cleaned_data