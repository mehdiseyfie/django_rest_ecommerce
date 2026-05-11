from ecommerce.cart.models import Cart 
from django.db import transaction 
from ecommerce.users.models import Profile 




@transaction.atomic
def get_or_create_cart(customer:Profile) -> Cart: 
    try:
        cart = Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        cart = Cart.objects.create(customer=customer) 
    
    return cart 