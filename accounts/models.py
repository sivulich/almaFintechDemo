from django.db import models
from iso4217 import raw_table


class Account(models.Model):
    ''' Account model
    Attributes:
        id          Unique identifier of account
        currency    ISO4217 currency of account
        balance     Balance of account presented in micro units to avoid float imprecision
    '''

    CURRENCY_CHOICES = (
        (key, raw_table['CcyNm'])
        for key in raw_table if key is not None  # Bug in iso4217 includes a key with value None
    )
    id = models.BigAutoField(primary_key=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.BigIntegerField(default=0)


class Transfer(models.Model):
    ''' Wire transfer model, allows to set origin_balance and destination_balance for multi-currency support
    Attributes:
        id                          Unique identifier of transfer
        date                        Date of the transfer, auto generated when creating the transfer
        origin                      Origin account of the transfer
        origin_balance              Origin account balance in micro units, forced to be positive to enforce direction
                                    of transfer.
        destination                 Destination account
        destination_balance        Destination account balance in micro units, forced to be positive to enforce
                                    direction of transfer.
        cancelled                   Allows to cancel the transfer and return the balance to origin account.
    '''

    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    origin = models.ForeignKey(Account, on_delete=models.SET_NULL)
    origin_balance = models.PositiveBigIntegerField(default=0)
    destination = models.ForeignKey(Account, on_delete=models.SET_NULL)
    destination_balance = models.PositiveBigIntegerField(default=0)
    cancelled = models.BooleanField(default=True)


