from django.db import transaction 
from .models import BaseUser, Profile


def create_profile(*, user:BaseUser) -> Profile:
    return Profile.objects.create(user=user)

def create_user(*, email:str, phone:str, 
                first_name:str, last_name:str, address: str | None,
                password:str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, phone=phone, last_name= last_name, first_name=first_name, address=address,  password=password) #type: ignore


@transaction.atomic
def register(*,  email:str, phone:str, 
                first_name:str, last_name:str, address: str | None,
                password:str) -> BaseUser:

    user = create_user(email=email, phone=phone, 
                       first_name=first_name, 
                       last_name=last_name,
                       address=address,
                       password=password)
    create_profile(user=user)

    return user
