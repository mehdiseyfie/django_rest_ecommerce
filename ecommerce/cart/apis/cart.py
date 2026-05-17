from sys import exception

from requests import delete
from rest_framework import status, serializers 
from rest_framework.response import Response 
from rest_framework.views import APIView
from sentry_sdk import serializer 
from ecommerce.cart.models import Cart, CartItem 
from drf_spectacular.utils import extend_schema 
from ecommerce.users.selectors import get_profile 
from ecommerce.cart.selectors.cart import (get_cart_by_customer, get_cart_by_slug, get_cart_item_by_slug)
from ecommerce.cart.services.cart import (get_or_create_cart, add_item_to_cart, update_cart_item, remove_cart_item, clear_cart) 
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.authentication import JWTAuthentication
from ecommerce.products.models import Product 


class OutputCartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.SlugField(source="product.slug", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "slug",
            "product",
            "product_name",
            "product_slug",
            "quantity",
            "price",
            "total_price",
            )
    def get_total_price(self, obj):
        return obj.get_total_price_item()
    
class OutputCartSerializer(serializers.ModelSerializer):
    items = OutputCartItemSerializer(source="cartitems", many=True, read_only=True)
    email = serializers.EmailField(source="customer.user.email", read_only=True)

    class Meta:
        model = Cart
        fields = (
                "id",
                "slug",
                "email",
                "items",
                "total_price",
                "total_items",
                "is_active",
                "is_ordered",
            )

class CartApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    class InputAddItemSerializer(serializers.Serializer):
        product = serializers.SlugRelatedField(
            queryset=Product.objects.all(),
            slug_field="slug"
        )
        quantity = serializers.IntegerField(min_value=1, default=1)

        def validate_product(self, value: Product):
            """Check stock availability"""
            if value.stock <= 0:
                raise serializers.ValidationError("This product is out of stock.")
            return value 
    
    class InputUpdateItemSerializer(serializers.Serializer): 
        quantity = serializers.IntegerField() 


    @extend_schema(responses=OutputCartSerializer)
    def get(self, request, slug=None):
        customer = get_profile(user=request.user)
        if slug is not None:
            cart = get_cart_by_slug(slug=slug)
            if cart is None or cart.customer != customer:
                return Response(
                    {"error": "You don't have access to this cart."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            cart = get_cart_by_customer(customer=customer)
            if not cart:
                cart = get_or_create_cart(customer=customer)

        serializer = OutputCartSerializer(cart, context={"request": request})
        return Response(serializer.data)

    @extend_schema(request=InputAddItemSerializer, responses=OutputCartItemSerializer)
    def post(self, request):
        customer = get_profile(user=request.user)
        serializer = self.InputAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            cart = get_or_create_cart(customer=customer)
            item = add_item_to_cart(
                cart=cart,
                product=validated_data["product"],
                quantity=validated_data["quantity"],
            )
            output_serializer = OutputCartItemSerializer(
                item, context={"request": request}
            )
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)  
        
    @extend_schema(request=InputUpdateItemSerializer, responses=OutputCartItemSerializer)
    def patch(self, request, slug): 
        customer = get_profile(user=request.user) 
        serializer = self.InputUpdateItemSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try:
            cart = get_cart_by_customer(customer=customer) 
            if not cart: 
                return Response({"error": "cart is not found"}, status=status.HTTP_404_NOT_FOUND) 
            cart_item = get_cart_item_by_slug(cart=cart, slug=slug) 
            updated_item = update_cart_item(cart_item=cart_item, quantity=validated_data["quantity"]) 
            
        except exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST) 
        
        serializer = OutputCartItemSerializer(updated_item, context={"request": request}) 
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    @extend_schema(responses={204:None})
    def delete(self, request, slug):
        customer = get_profile(user=request.user)
        try:
            cart = get_cart_by_customer(customer=customer) 
            if not cart: 
                return Response({"error": "cart is not found."}, status=status.HTTP_404_NOT_FOUND) 
            cart_item = get_cart_item_by_slug(cart=cart, slug=slug) 
            remove_cart_item(cart_item=cart_item) 
            
        except exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_204_NO_CONTENT) 

class ClearCartApi(APIView): 
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated] 
    
    @extend_schema(responses={204:None})
    def delete(self, request): 
        customer = get_profile(user=request.user) 
        
        try: 
            cart = get_cart_by_customer(customer=customer) 
            if not cart: 
                return Response({"error": "cart is not exist."}, status=status.HTTP_404_NOT_FOUND) 
            clear_cart(cart) 
        except exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "cart cleared succesfully"} ,status=status.HTTP_204_NO_CONTENT) 
     