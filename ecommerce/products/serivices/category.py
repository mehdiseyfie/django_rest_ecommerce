from typing import Optional

from ecommerce.products.models import Category 
from django.db import transaction
from django.utils.text import slugify

@transaction.atomic
def create_category(*, name:str, description:str) -> Category:
        return Category.objects.create(
                                       name=name,
                                       description=description
                                       )
@transaction.atomic
def update_category(*, category: Category, name:Optional[str], description:Optional[str]) -> Category: 
        if name is not None:
                category.name = name 
                category.slug = slugify(category.name) 
        if description is not None: 
                category.description = description
        
        category.save()
        return category 
        
        

