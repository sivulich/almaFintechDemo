from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account


# Create your models here.
class Profile(models.Model):
    ''' Profile model, used to store the extra information the base user model does not have
        Attributes:
            user            User to whom this profile belongs.
            cuit            Unique tributary identification code.
            phone           User phone.
            company         User working company.
            accounts        Accounts to which this user has access to.
        '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cuit = models.CharField(max_length=14, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    company = models.CharField(max_length=32, blank=True, null=True)
    accounts = models.ManyToManyField(Account)
