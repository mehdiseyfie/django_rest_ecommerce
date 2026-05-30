from django.urls import path, include

urlpatterns = [
    path('users/', include('ecommerce.users.urls')),
    path('products/', include('ecommerce.products.urls')),
    path('cart/', include('ecommerce.cart.urls')),
    path('orders/', include('ecommerce.orders.urls')),
    path('authentication/', include('ecommerce.authentication.urls')),
]
