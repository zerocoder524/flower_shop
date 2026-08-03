from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    """Форма регистрации покупателя."""

    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=True,
    )

    email = forms.EmailField(
        label="Электронная почта",
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "email",
        )
        labels = {
            "username": "Логин",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже существует."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"].strip()
        user.email = self.cleaned_data["email"].strip().lower()

        if commit:
            user.save()

        return user