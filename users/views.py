from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignUpForm


def register(request):
    """Регистрация нового покупателя."""

    if request.user.is_authenticated:
        return redirect("catalog:product_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            messages.success(
                request,
                "Регистрация успешно завершена.",
            )

            return redirect("catalog:product_list")
    else:
        form = SignUpForm()

    return render(
        request,
        "users/register.html",
        {
            "form": form,
        },
    )
