from rest_framework import status, serializers
from rest_framework.response import Response 
from rest_framework.views import APIView 
from ecommerce.products.models import Product, Category 
from drf_spectacular.utils import extend_schema 
from ecommerce.products.selectors.product import (get_product_by_name, get_all_product) 

from ecommerce.products.serivices.product import create_product


class ProductApi(APIView):
    
    class InputProductSerializer(serializers.Serializer): 
        category = serializers.SlugRelatedField(
            queryset=Category.objects.all(), slug_field="slug"
        )
        name = serializers.CharField() 
        description = serializers.CharField() 
        price = serializers.DecimalField(max_digits=10, decimal_places=2)
        stock = serializers.IntegerField() 
        available = serializers.BooleanField()
        newest_product = serializers.BooleanField()
        
        def validate_name(self, value): 
            if hasattr(self, "instance") and self.instance and self.instance.name == value: 
                return value 
            
            if Product.objects.filter(name__iexact=value).exists(): 
                raise serializers.ValidationError("This Product already exists.") 
            return value 
        
    class OutputProductSerializer(serializers.ModelSerializer):  
        category = serializers.CharField(source="category.name")
        
        class Meta: 
            model = Product
            fields = (
                "id",
                "category",
                "name", 
                "slug",
                "description", 
                "price",
                "stock",
                "available",
                "newest_product"
            ) 
        read_only_fields = ("slug",)
        
    @extend_schema(responses=OutputProductSerializer(many=True))
    def get(self, request, name=None): 
        if name is not None:
            product = get_product_by_name(name=name) 
            serializer = self.OutputProductSerializer(product,
                                                      context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK) 
        products = get_all_product() 
        serializer = self.OutputProductSerializer(products,many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK) 
        
        
    @extend_schema(request=InputProductSerializer, responses=OutputProductSerializer) 
    def post(self,request): 
        
        serializer = self.InputProductSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data  
        
        try: 
            new_product = create_product(
                category=validated_data.get("category"),
                name=validated_data.get("name"), 
                description=validated_data.get("description"),
                price=validated_data.get("price"), 
                stock=validated_data.get("stock"), 
                available=validated_data.get("available"),
                newest_product=validated_data.get("newest_product")
            ) 
            serializer = self.OutputProductSerializer(
                new_product, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        except Exception as ex: 
            return Response({"error": str(ex)}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        