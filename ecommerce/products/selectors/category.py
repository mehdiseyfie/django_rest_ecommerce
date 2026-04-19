from typing import Optional

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from ecommerce.products.models import Category 
from django.db.models import QuerySet 

def get_category_by_name(name:str) -> Category: 
    return get_object_or_404(Category, name=name)

def get_all_category() -> QuerySet[Category]: 
    return Category.objects.all() 


    
    