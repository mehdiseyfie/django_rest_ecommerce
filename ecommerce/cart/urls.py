from django.urls import path
from ecommerce.cart.apis.cart import CartApi , CartItemApi


urlpatterns = [
    path("items/", CartItemApi.as_view(), name="add-item-to-cart"),
    path('', CartApi.as_view(), name='cart-detail'),
    path('<slug:slug>/', CartApi.as_view(), name='cart-by-slug'), 
]