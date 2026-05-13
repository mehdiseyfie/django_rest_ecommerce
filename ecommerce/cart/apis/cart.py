from rest_framework import status, serializers 
from rest_framework.response import Response 
from rest_framework.views import APIView 
from ecommerce.cart.models import Cart, CartItem 
from drf_spectacular.utils import extend_schema 
from ecommerce.users.selectors import get_profile 
from ecommerce.cart.selectors.cart import (get_cart_by_customer, get_cart_by_slug)
from ecommerce.cart.services.cart import (get_or_create_cart, add_item_to_cart) 
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
            "product",
            "product_name", 
            "product_slug", 
            "quantity",
            "price",
            "total_price"
            
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
                "is_ordered"
            )  

class CartApi(APIView): 
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=OutputCartSerializer) 
    def get(self, request, slug=None): 

        customer = get_profile(user=request.user) 
        if slug is not None: 
            cart = get_cart_by_slug(slug=slug)
            if cart is not None:
                if cart.customer != customer:
                    return Response({"error": "you don't have access to this cart."}, status=status.HTTP_403_FORBIDDEN) 
        else: 
            cart = get_cart_by_customer(customer=customer) 
            if not cart: 
                cart = get_or_create_cart(customer=customer) 
            
        serializer = OutputCartSerializer(cart, context={"request", request})
        return Response(serializer.data) 
            
class CartItemApi(APIView): 
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated] 
    
    class InputAddItemSerializer(serializers.Serializer):
        product = serializers.SlugRelatedField(queryset=Product.objects.all(), slug_field="slug") 
        quantity = serializers.IntegerField(min_value=1, default=1) 
        
        def validate_product(self, value):
            if Product.objects.filter(slug__iexact=value.slug).exists(): 
                if value.stock > 0: 
                    return value 
                else: 
                    raise ValueError({"error": "this product stocks it is not enought"})
            else:
                raise ValueError({"error": "this product it's not exist."}) 
        
            
    @extend_schema(request=InputAddItemSerializer, responses=OutputCartItemSerializer)
    def post(self, request): 
        customer = get_profile(user=request.user)
        serializer = self.InputAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try: 
            cart = get_or_create_cart(customer=customer) 
            item = add_item_to_cart(cart=cart, product=validated_data.get("product"), quantity=validated_data.get("quantity"), 
                                        ) 
            serializer = OutputCartItemSerializer(item, context={"request": request}) 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        except Exception as ex: 
            
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            
            
        
        
        
        
         
        
        
         
        
        
        
    
            
        
        
        
        
        
        
        
        
        
            
                   
            