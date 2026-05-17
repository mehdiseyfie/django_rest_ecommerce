from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView 

class UserIsStuffOrReadOnly(BasePermission): 
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS: 
            return True 
        return request.user.is_authenticated and request.user.is_superuser #type: ignore
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in SAFE_METHODS: 
            return True 
        return request.user.is_authenticated and request.user.is_superuser #type: ignore
    
    
    
        