from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from catalog.models import Product

from .forms import OrderForm
from .models import Order
from .services import (
    ShopClosedError,
    create_order,
    get_shop_hours,
    is_shop_open,
)


@login_required
def order_create(request, product_id):
    """Оформление заказа на выбранный товар."""

    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True,
    )

    if request.method == "POST":
        form = OrderForm(
            request.POST,
            product=product,
        )

        if form.is_valid():
            try:
                order = create_order(
                    form=form,
                    user=request.user,
                    product=product,
                )
            except ShopClosedError as error:
                form.add_error(
                    None,
                    str(error),
                )
            except ValidationError as error:
                form.add_error(
                    None,
                    "; ".join(error.messages),
                )
            else:
                messages.success(
                    request,
                    f"Заказ №{order.pk} успешно оформлен.",
                )

                return redirect(
                    "orders:order_success",
                    pk=order.pk,
                )
    else:
        initial_name = (
            request.user.get_full_name()
            or request.user.username
        )

        form = OrderForm(
            product=product,
            initial={
                "customer_name": initial_name,
                "quantity": 1,
            },
        )

    open_time, close_time = get_shop_hours()

    return render(
        request,
        "orders/order_form.html",
        {
            "form": form,
            "product": product,
            "shop_open": is_shop_open(),
            "shop_hours": (
                f"{open_time.strftime('%H:%M')}–"
                f"{close_time.strftime('%H:%M')}"
            ),
        },
    )


@login_required
def order_success(request, pk):
    """Подтверждение заказа."""

    order = get_object_or_404(
        Order.objects.select_related(
            "product",
            "user",
        ),
        pk=pk,
        user=request.user,
    )

    return render(
        request,
        "orders/order_success.html",
        {"order": order},
    )