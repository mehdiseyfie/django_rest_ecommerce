import decimal
from typing import Optional
from ecommerce.products.models import Category, Product
from django.db import transaction
from django.utils.text import slugify

@transaction.atomic
def create_product(
    *,
    category: Category,
    name: str,
    description: str,
    price: str,
    stock: str,
    available: bool,
    newest_product: bool
) -> Product:
    return Product.objects.create(
        category=category,
        name=name,
        description=description,
        price=price,
        stock=stock,
        available=available,
        newest_product=newest_product
    )

@transaction.atomic
def update_product(
    *,
    product: Product,
    category: Optional[Category] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[str] = None,
    stock: Optional[str] = None,
    available: Optional[bool] = None,
    newest_product: Optional[bool] = None
) -> Product:
    if category is not None:
        product.category = category
    if name is not None:
        product.name = name
        product.slug = slugify(name)
    if description is not None:
        product.description = description
    if price is not None:
        product.price = decimal.Decimal(price)
    if stock is not None:
        product.stock = int(stock)
    if available is not None:
        product.available = bool(available)
    if newest_product is not None:
        product.newest_product = bool(newest_product)

    product.save()
    return product