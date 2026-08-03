from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from catalog.models import Product
from .models import Order


@override_settings(
    SHOP_OPEN_TIME="00:00:00",
    SHOP_CLOSE_TIME="23:59:59",
)
class OrderViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="StrongPassword123!",
        )

        self.product = Product.objects.create(
            name="Букет роз",
            price=Decimal("3500.00"),
            is_available=True,
        )

    def test_order_page_requires_login(self):
        response = self.client.get(
            reverse(
                "orders:order_create",
                args=[self.product.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_valid_order_is_created(self):
        self.client.login(
            username="customer",
            password="StrongPassword123!",
        )

        response = self.client.post(
            reverse(
                "orders:order_create",
                args=[self.product.pk],
            ),
            {
                "quantity": 2,
                "customer_name": "Иван Иванов",
                "phone": "+7 900 000-00-00",
                "recipient_name": "Анна",
                "delivery_address": "Тестовый адрес",
                "delivery_date": (
                    timezone.localdate()
                    + timedelta(days=1)
                ).isoformat(),
                "delivery_time": "15:00",
                "comment": "",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.product,
            self.product,
        )

        self.assertEqual(
            order.total_price,
            Decimal("7000.00"),
        )