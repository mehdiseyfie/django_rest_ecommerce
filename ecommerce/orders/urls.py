from django.urls import path 
from ecommerce.orders.apis.order import OrderApi 


urlpatterns = [
    path("", OrderApi.as_view(), name="order-list"),
    path("<slug:slug>/", OrderApi.as_view(), name="order-detail"),
    
]
