from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager as BUM
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from ecommerce.common.models import BaseModel


class BaseUserManager(BUM):
    def create_user(self, first_name, last_name, email, phone, is_active=True, is_admin=False, password=None, address=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not phone:
            raise ValueError("The given phone number must be set")

        user = self.model(email=self.normalize_email(email.lower()), phone=phone, first_name=first_name, last_name=last_name, is_active=is_active, is_admin=is_admin, address=address) 

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, phone=None,address=None, first_name=None, last_name=None):
        # For superuser creation via command line, phone is optional
        if not phone:
            # Prompt for phone if not provided
            phone = input("Phone number: ")
        
        user = self.create_user( 
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_admin=True,
            password=password,
            address=address
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(verbose_name="email address", unique=True)
    phone = PhoneNumberField(_("phone number"), unique=True) 
    address = models.TextField(blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True) 
        

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]
    
    class Meta:
            verbose_name = _("user")
            verbose_name_plural = _("users") 
            
    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.is_admin


class Profile(BaseModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
    def __str__(self):
        return f"{self.user.email} Profile"
