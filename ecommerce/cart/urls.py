from django.urls import path
from ecommerce.cart.apis.cart import  CartApi, ClearCartApi


urlpatterns = [
    path("items/", CartApi.as_view(), name="add-item-to-cart"),
    path("clear/", ClearCartApi.as_view(), name="clear-cart"),
    path('', CartApi.as_view(), name='cart-detail'),
    path('<slug:slug>/', CartApi.as_view(), name='cart-by-slug')
]