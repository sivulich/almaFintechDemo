# Alma Fintech Demo
This project was developed as a demonstration to Alma Fintech.

## Goal
The goal was to develop a simple electronic wallet model where you could create, manage and delete accounts, make 
transfers to them and revert transfers.

## Project structure
### Accounts
This django app handles all the login corresponding to managment of accounts and transfers between them.

#### models.py
For this two database models where created in models.py:
```python
class Account(models.Model):
    '''
    Account model
    Attributes:
        id          Unique identifier of account
        currency    ISO4217 currency of account
        balance     Balance of account presented in micro units to avoid float imprecision
    '''

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

```
The transfer model was extended in functionality to modify the accounts upon creation and when its cancelled.

This models get stored in an sql database of choice, for this demo the default sqlite3 database is used.


#### serializers.py
This file handles the serialization of the Account and Transfer model.

### views.py


### Considerations

 - User can only revert received transfers. 
 - User can only create a transfer between accounts of same currency.
 - Admins have access to every part 