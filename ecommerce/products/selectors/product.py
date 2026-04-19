from ecommerce.products.models import Product 
from django.core.exceptions import ValidationError 
from django.db.models import QuerySet

def get_product_by_name(name:str) -> Product: 
    try: 
        product = Product.objects.get(name=name) 
        return product
    except Product.DoesNotExist:
        raise ValidationError("product doesn't exist.") 

def get_all_product() -> QuerySet[Product]: 
    return Product.objects.all()
    