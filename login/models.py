from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cuit = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    company = models.CharField(max_length=32, blank=True, null=True)
    accounts = models.ManyToManyField(Account)
