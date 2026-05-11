from ecommerce.users.models import Profile, BaseUser 
from django.shortcuts import get_object_or_404
from ecommerce.cart.models import Cart 
from typing import Optional
from ecommerce.users.models import Profile


def get_cart_by_slug(slug:str) -> Optional[Cart]: 
    return get_object_or_404(Cart, slug=slug)
        
    

def get_cart_by_customer(customer:Profile) -> Optional[Cart]: 
    try:
        return Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        return None 