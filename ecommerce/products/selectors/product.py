from ecommerce.products.models import Product
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

def get_product_by_slug(slug: str) -> Product:
    return get_object_or_404(Product, slug=slug)

def get_all_product() -> QuerySet[Product]:
    return Product.objects.all()