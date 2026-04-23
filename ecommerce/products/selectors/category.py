from django.shortcuts import get_object_or_404
from ecommerce.products.models import Category
from django.db.models import QuerySet

def get_category_by_slug(slug: str) -> Category:
    return get_object_or_404(Category, slug=slug)

def get_all_category() -> QuerySet[Category]:
    return Category.objects.all()