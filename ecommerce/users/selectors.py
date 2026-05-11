from .models import Profile, BaseUser 
from django.shortcuts import get_object_or_404

def get_profile(user:BaseUser) -> Profile:
    return get_object_or_404(Profile, user=user)
