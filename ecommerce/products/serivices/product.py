from ecommerce.products.models import Product 
from django.db import transaction 

@transaction.atomic
def create_product(*, category:str, name:str,description:str, 
                   price:str,stock:str, available:str,
                   newest_product:str) -> Product: 
    
    return Product.objects.create(category=category, 
                                  name=name,
                                  description=description, 
                                  price=price,
                                  stock=stock, 
                                  available=available,
                                  newest_product=newest_product) 