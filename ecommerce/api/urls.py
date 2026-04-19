from django.urls import path, include

urlpatterns = [
    path('users/', include('ecommerce.users.urls')),
    path('products/', include('ecommerce.products.urls')),
]
