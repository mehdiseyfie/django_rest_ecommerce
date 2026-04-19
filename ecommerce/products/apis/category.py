from rest_framework import serializers 
from ecommerce.products.models import Category 
from rest_framework.response import Response 
from rest_framework.views import APIView 
from rest_framework import status 
from drf_spectacular.utils import extend_schema 
from ecommerce.products.selectors.category import (
                                                   get_category_by_name,
                                                   get_all_category
                                                   ) 

from ecommerce.products.serivices.category import (create_category,
                                                   update_category)

class CategoryApi(APIView):
    
    class InputCategorySerializer(serializers.Serializer): 
        name = serializers.CharField()
        description = serializers.CharField() 
        
        def validate_name(self, value):
            if hasattr(self, 'instance') and self.instance and self.instance.name == value:
                return value  
            
            if Category.objects.filter(name__iexact=value).exists(): 
                raise serializers.ValidationError("This category already exists.")
            return value 
    
    class OutputSerializer(serializers.ModelSerializer): 
        
        class Meta: 
            model = Category
            fields = (
                "name", "slug", "description"
            ) 
    @extend_schema(responses=OutputSerializer(many=True))
    def get(self, request, name=None): 
        
        if name: 
            try: 
                category = get_category_by_name(name=name) 
                serializer = self.OutputSerializer(instance=category)
                return Response(serializer.data, status=status.HTTP_200_OK) 
            except Exception as ex: 
                return Response({"error": str(ex)}, status=status.HTTP_404_NOT_FOUND)
        
        categories = get_all_category() 
        serializer = self.OutputSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(request=InputCategorySerializer, 
                   responses=OutputSerializer) 
    def post(self, request): 
        serializer = self.InputCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data 
        
        try:
            category = create_category(name=validated_data.get("name"),
                                description=validated_data.get("description")) 
            serializer = self.OutputSerializer(category, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as ex:
                return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": str(ex)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(request=InputCategorySerializer, responses=OutputSerializer)
    def patch(self, request, name):
        category = get_category_by_name(name=name) 
        serializer = self.InputCategorySerializer(instance=category, 
                                                  data=request.data,
                                                  partial=True
                                                  ) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        try:
            category = update_category(
                                    category=category,
                                    name=validated_data.get("name"),
                                    description=validated_data.get("description")) 
            serializer = self.OutputSerializer(
                                                    category, 
                                                    context={"request":request}
                                                ) 
            return Response(serializer.data, status=status.HTTP_200_OK) 
        except Exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(responses={204:None})
    def delete(self, request, name): 
        try:
            category = get_category_by_name(name=name) 
            category.delete() 
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except Exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


        
        
        
        
        
        
        
        
        
         
        
        























