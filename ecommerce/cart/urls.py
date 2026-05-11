from django.urls import path
from ecommerce.cart.apis.cart import CartApi 


urlpatterns = [
    path('', CartApi.as_view(), name='cart-detail'),
    path('<slug:slug>/', CartApi.as_view(), name='cart-by-slug')
]