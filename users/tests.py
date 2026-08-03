from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse


class UserAuthenticationTests(TestCase):
    """Тесты регистрации, входа и выхода пользователей."""

    def setUp(self):
        self.User = get_user_model()

        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.logout_url = reverse("users:logout")
        self.catalog_url = reverse("catalog:product_list")

        self.password = "FlowerShop2026!Test"

    def registration_data(self, **overrides):
        """Возвращает корректный набор регистрационных данных."""

        data = {
            "username": "Customer1",
            "first_name": "Иван",
            "email": "customer1@example.com",
            "password1": self.password,
            "password2": self.password,
        }

        data.update(overrides)

        return data

    def test_successful_registration_creates_user(self):
        """Корректная регистрация создаёт пользователя."""

        response = self.client.post(
            self.register_url,
            self.registration_data(),
        )

        self.assertRedirects(
            response,
            self.catalog_url,
        )

        user = self.User.objects.get(
            username="Customer1",
        )

        self.assertEqual(
            user.first_name,
            "Иван",
        )

        self.assertEqual(
            user.email,
            "customer1@example.com",
        )

        self.assertTrue(user.is_active)

    def test_registration_saves_hashed_password(self):
        """Пароль сохраняется через механизм хеширования Django."""

        self.client.post(
            self.register_url,
            self.registration_data(),
        )

        user = self.User.objects.get(
            username="Customer1",
        )

        self.assertNotEqual(
            user.password,
            self.password,
        )

        self.assertTrue(
            user.check_password(self.password)
        )

    def test_user_is_logged_in_after_registration(self):
        """После регистрации пользователь автоматически входит."""

        self.client.post(
            self.register_url,
            self.registration_data(),
        )

        self.assertIn(
            SESSION_KEY,
            self.client.session,
        )

    def test_duplicate_email_is_rejected(self):
        """Нельзя зарегистрировать второй аккаунт с тем же email."""

        self.User.objects.create_user(
            username="ExistingUser",
            email="customer1@example.com",
            password=self.password,
        )

        response = self.client.post(
            self.register_url,
            self.registration_data(),
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.User.objects.filter(
                email="customer1@example.com",
            ).count(),
            1,
        )

        self.assertContains(
            response,
            (
                "Пользователь с такой электронной "
                "почтой уже существует."
            ),
        )

    def test_different_passwords_are_rejected(self):
        """Регистрация отклоняется при разных паролях."""

        response = self.client.post(
            self.register_url,
            self.registration_data(
                password2="AnotherPassword2026!",
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            self.User.objects.filter(
                username="Customer1",
            ).exists()
        )

    def test_regular_user_can_log_in(self):
        """Обычный пользователь может войти на сайт."""

        user = self.User.objects.create_user(
            username="Customer1",
            email="customer1@example.com",
            password=self.password,
        )

        response = self.client.post(
            self.login_url,
            {
                "username": "Customer1",
                "password": self.password,
            },
        )

        self.assertRedirects(
            response,
            self.catalog_url,
        )

        self.assertEqual(
            int(self.client.session[SESSION_KEY]),
            user.pk,
        )

    def test_user_can_log_out(self):
        """Авторизованный пользователь может выйти."""

        user = self.User.objects.create_user(
            username="Customer1",
            email="customer1@example.com",
            password=self.password,
        )

        self.client.force_login(user)

        response = self.client.post(
            self.logout_url,
        )

        self.assertRedirects(
            response,
            self.catalog_url,
        )

        self.assertNotIn(
            SESSION_KEY,
            self.client.session,
        )