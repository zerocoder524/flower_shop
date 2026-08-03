from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductViewsTests(TestCase):
    def setUp(self):
        self.available_product = Product.objects.create(
            name="Доступный букет",
            price=Decimal("3000.00"),
            is_available=True,
        )

        self.hidden_product = Product.objects.create(
            name="Недоступный букет",
            price=Decimal("4000.00"),
            is_available=False,
        )

    def test_catalog_displays_only_available_products(self):
        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertContains(
            response,
            "Доступный букет",
        )

        self.assertNotContains(
            response,
            "Недоступный букет",
        )

    def test_unavailable_product_detail_returns_404(self):
        response = self.client.get(
            reverse(
                "catalog:product_detail",
                args=[self.hidden_product.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )