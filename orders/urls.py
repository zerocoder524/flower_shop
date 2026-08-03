from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path(
        "create/<int:product_id>/",
        views.order_create,
        name="order_create",
    ),
    path(
        "success/<int:pk>/",
        views.order_success,
        name="order_success",
    ),
]