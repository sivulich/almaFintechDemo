from django.db import models, NotSupportedError
from iso4217 import raw_table
from django.db.models import F
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.core.cache import cache


class Account(models.Model):
    ''' Account model
    Attributes:
        id          Unique identifier of account
        currency    ISO4217 currency of account
        balance     Balance of account presented in micro units to avoid float imprecision
    '''

    CURRENCY_CHOICES = (
        (key, raw_table[key]['CcyNm'])
        for key in raw_table if key is not None  # Bug in iso4217 includes a key with value None
    )
    id = models.BigAutoField(primary_key=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.BigIntegerField(default=0)


class Transfer(models.Model):
    ''' Wire transfer model, origin account and destination account must be same currency
    Attributes:
        id                          Unique identifier of transfer
        date                        Date of the transfer, auto generated when creating the transfer
        origin                      Origin account of the transfer
        destination                 Destination account
        balance                     Destination account balance in micro units, forced to be positive to enforce
                                    direction of transfer.
        cancelled                   Allows to cancel the transfer and return the balance to origin account.
    '''

    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    origin = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='out_transfers')
    destination = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='in_transfers')
    balance = models.PositiveBigIntegerField(default=0)
    cancelled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Check for creation and update data
        if self.id is None:
            with transaction.atomic():
                # Disable for testing purposes, a cache backend must be setup
                # Obtain locks for accounts, to a valid state and fix races between transfers
                # Should be used in conjunction with REDIS as cache backend
                # with cache.lock(f'account.{self.origin_id}'):
                #     with cache.lock(f'account.{self.destination_id}'):

                # Check for same currency and available funds
                if not self.origin.currency == self.destination.currency:
                    raise ValidationError('Origin currency must match destination currency')
                if not Account.objects\
                    .filter(id=self.origin_id, balance__gte=self.balance).exists():
                    raise ValidationError('Origin account has insufficient funds')

                Account.objects.filter(id=self.origin_id).update(
                    balance=F('balance')-self.balance)
                Account.objects.filter(id=self.destination_id).update(
                    balance=F('balance') + self.balance)
                return super(Transfer, self).save(*args, **kwargs)
        else:
            # Assume an admin or server made an edit, no need to make conciliation
            return super(Transfer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.cancelled is True:
            raise ValidationError('Transfer already cancelled')
        with transaction.atomic():
            # Disable for testing purposes, a cache backend must be setup
            # Obtain locks for accounts, to a valid state and fix races between transfers
            # Should be used in conjunction with REDIS as cache backend
            # with cache.lock(f'account.{self.origin_id}'):
            #     with cache.lock(f'account.{self.destination_id}'):

            # Check for available funds to return transfer
            if not Account.objects.filter(id=self.destination_id, balance__gte=self.balance).exists():
                raise ValidationError('Destination account has insufficient funds')

            Account.objects.filter(id=self.origin_id).update(
                balance=F('balance')+self.balance)
            Account.objects.filter(id=self.destination_id).update(
                balance=F('balance') - self.balance)
            self.cancelled = True
            self.save()


