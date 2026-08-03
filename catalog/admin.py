from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "is_available",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "is_available",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "price",
        "is_available",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )