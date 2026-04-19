from django.urls import path
from ecommerce.products.apis.category import CategoryApi
from ecommerce.products.apis.product import ProductApi

urlpatterns = [
     path("categories/<str:name>/", CategoryApi.as_view(), name="category-detail"),
    path("categories/", CategoryApi.as_view(), name="category-list"), 
    path("<str:name>/", ProductApi.as_view(), name="product-detail"), 
    path("", ProductApi.as_view(), name="products-list")
]