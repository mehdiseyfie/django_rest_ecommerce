from ecommerce.cart.models import Cart, CartItem
from django.db import transaction 
from ecommerce.products.models import Product
from ecommerce.users.models import Profile 
from django.core.exceptions import ValidationError 
from decimal import Decimal




@transaction.atomic
def get_or_create_cart(customer:Profile) -> Cart: 
    try:
        cart = Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        cart = Cart.objects.create(customer=customer) 
    
    return cart 

@transaction.atomic
def add_item_to_cart(cart: Cart, product: Product, quantity:int) -> CartItem: 
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    if product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {product.stock}")
    try: 
        cart_item = CartItem.objects.get(cart=cart, product=product) 
        old_quantity = cart_item.quantity 
        old_price = cart_item.price 
        total_quantity = old_quantity + quantity 
        cart_item.quantity = total_quantity
        cart_item.save(old_quantity=old_quantity, old_price=old_price) 
    except CartItem.DoesNotExist: 
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)  
        
    return cart_item
         
@transaction.atomic
def update_cart_item(cart_item:CartItem, quantity:int) -> CartItem:
    if quantity <= 0:
        raise ValidationError("Quantity must be positive") 
    if cart_item.product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {cart_item.product.stock}")  
    
    old_quantity = cart_item.quantity 
    old_price = cart_item.price 
    
    cart_item.quantity = quantity 
    
    cart_item.save(old_quantity=old_quantity, old_price=old_price)
    
    return cart_item 
    
    
@transaction.atomic
def remove_cart_item(cart_item:CartItem)-> None: 
    cart_item.delete()

@transaction.atomic
def clear_cart(cart:Cart) -> None: 
    cart.cartitems.all().delete() #type: ignore 
    cart.total_items = 0 
    cart.total_price = Decimal("0.00")
    cart.save()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        