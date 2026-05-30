from rest_framework.views import APIView
from rest_framework import serializers 
from rest_framework.response import Response 
from rest_framework import status 
from ecommerce.cart.selectors.cart import (get_cart_by_customer)
from ecommerce.orders.models import (Order, OrderItem, Payment, ShippingAddress)
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.authentication import JWTAuthentication 
from phonenumber_field.serializerfields import PhoneNumberField 
from drf_spectacular.utils import extend_schema
from ecommerce.users.selectors import get_profile 
from ecommerce.orders.selectors.order import (get_customer_order_by_slug, get_all_orders_by_customer, get_shipping_addresses, get_default_shipping_address, get_shipping_address_by_id, get_order_by_customer, get_order_item_by_slug)
from ecommerce.cart.models import (Cart, CartItem) 
from ecommerce.orders.services.order import (create_order_from_cart, update_order_item)


class OutputOrderItemSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.SlugField(source="product.slug", read_only=True)
    total_price = serializers.SerializerMethodField()
    
    
    class Meta: 
        model = OrderItem
        fields = (
            "id",
            "slug",
            "product_name",
            "product_slug",
            "product",
            "quantity",
            "price", 
            "total_price"
            
        ) 
    
    def get_total_price(self, obj): 
        return obj.get_total_price_item() 
    
class OutpuPaymentSerializer(serializers.ModelSerializer): 
    
    class Meta: 
        model = Payment 
        fields = "__all__"

class OutputShippingAddressSerializer(serializers.ModelSerializer):
    """Output serializer for shipping address"""
    
    class Meta:
        model = ShippingAddress
        fields = (
            "id",
            "first_name",
            "last_name",
            "company",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "is_default",
            "created_at"
        )
        


class OutputOrderSerializer(serializers.ModelSerializer): 
    items = OutputOrderItemSerializer(source="orderitems", many=True, read_only=True) 
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    customer_phone = PhoneNumberField(source="customer.user.phone", read_only=True)
    cart_slug = serializers.SlugField(source="cart.slug", read_only=True) 
    total_amount = serializers.SerializerMethodField() 
    payment = OutpuPaymentSerializer(read_only=True) 
    shipping_address = OutputShippingAddressSerializer(read_only=True) 
    billing_address = OutputShippingAddressSerializer(read_only=True) 
    
    
    
    class Meta:
        model = Order
        fields = (
            "id",
            "slug",
            "items",
            "customer_email",
            "customer_phone",
            "cart_slug",
            "payment",
            "total_amount",
            "total_items", 
            "status",
            "payment_status",
            "payment_gateway",
            "tracking_number",
            "shipping_address", 
            "billing_address", 
            "shipping_method", 
            "shipping_cost", 
            "tax_amount"
            
            
        )
        
    def get_total_amount(self, obj): 
        return obj.get_total_amount() 
    
class OrderApi(APIView): 
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated] 

    class InputCreateOrderSerializer(serializers.Serializer):
        
        shipping_method = serializers.ChoiceField(choices=['standard', 
                                                                   'express', 
                                                                   'overnight', 
                                                                   'pickup'],
                                                          default='standard'
                                                          )
        discount_code = serializers.CharField(required=False,
                                          allow_blank=True, 
                                          max_length=50) 
        shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
        billing_address_id = serializers.IntegerField(required=False, allow_null=True) 
    
    class InputUpdateOrderSerializer(serializers.Serializer): 
        quantity = serializers.IntegerField()
        
        
    

    @extend_schema(responses=OutputOrderSerializer(many=True))
    def get(self, request, slug=None): 
        customer = get_profile(user=request.user) 
        if slug: 
            order = get_customer_order_by_slug(customer=customer, slug=slug) 
            if not order: 
                return Response({"error": "not found any order with this slug."}, status=status.HTTP_404_NOT_FOUND) 
            serializer = OutputOrderSerializer(order, context={"request": request}) 
            return Response(serializer.data, status=status.HTTP_200_OK) 
        
        orders = get_all_orders_by_customer(customer=customer) 
        if not orders: 
            return Response({"error": "not found any order for you."}, status=status.HTTP_404_NOT_FOUND) 
        serializer = OutputOrderSerializer(orders, many=True, context={"request": request}) 
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    
    @extend_schema(request=InputCreateOrderSerializer, responses=OutputOrderItemSerializer) 
    def post(self, request): 
        customer = get_profile(user=request.user) 
        serializer = self.InputCreateOrderSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data  
        
        try: 
            cart = get_cart_by_customer(customer=customer) 
            if not cart: 
                return Response({"error": "you don't have cart."}, status=status.HTTP_404_NOT_FOUND) 
            
            shipping_address = None
            billing_address = None
            
            if validated_data.get('shipping_address_id'): #type: ignore
                shipping_address = get_shipping_address_by_id(
                    address_id=validated_data['shipping_address_id'],  # type: ignore
                    customer=customer
                )
            else:
                # Use default address
                shipping_address = get_default_shipping_address(customer=customer)
            
            if validated_data.get('billing_address_id'): #type: ignore
                billing_address = get_shipping_address_by_id(
                    address_id=validated_data['billing_address_id'],  # type: ignore
                    customer=customer
                )
            
            order = create_order_from_cart(customer=customer, cart=cart, shipping_method=validated_data.get("shipping_method"), discount_code=validated_data.get("discount_code"), shipping_address= shipping_address, billing_address=billing_address) 
            
        except Exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST) 
        
        serializer = OutputOrderSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    
    @extend_schema(request=InputUpdateOrderSerializer, responses=OutputOrderItemSerializer) 
    def patch(self, request, slug): 
        customer = get_profile(user=request.user) 
        serializer = self.InputUpdateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try: 
            order = get_order_by_customer(customer=customer) 
            if not order: 
                return Response({'error': 'not found order for you'}, status=status.HTTP_404_NOT_FOUND) 
            order_item = get_order_item_by_slug(customer=customer, slug=slug) 
            update_item = update_order_item(order_item=order_item, quantity=validated_data["quantity"]) 
        except Exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST) 
        
        serializer = OutputOrderItemSerializer(update_item, partial=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    
        
    
    
    
    
    
    
    
    



