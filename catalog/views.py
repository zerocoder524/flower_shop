from django.views.generic import DetailView, ListView

from .models import Product


class ProductListView(ListView):
    """Страница со списком доступных товаров."""

    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True,
        ).order_by("name")


class ProductDetailView(DetailView):
    """Страница с подробной информацией о товаре."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True,
        )