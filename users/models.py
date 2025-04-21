from .managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('individual', 'Individual'),
        ('org_admin', 'Organization Admin'),
    )
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    is_premium = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLES)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_verification_email_sent = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Organization(models.Model):
    ENTITY_CHOICES = [
        ("FA", "Federal Agency"),
        ("PV", "Private Company")
    ]
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=2, choices=ENTITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="profiles",
        null=True, blank=True)
