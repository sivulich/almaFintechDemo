# Alma Fintech Demo
This project was developed as a demonstration to Alma Fintech.

## Goal
The goal was to develop a simple electronic wallet model where you could create, manage and delete accounts, make 
transfers to them and revert transfers.

## Technologies
The following technologies where used:
 - Django Web Development Framework
 - Django Rest Framework
 - JWT authentication

## Running the project
To run the project after cloning the project, creating a python environment is recommended:
```
cd almaFintech
python3 -m venv venv
source ./venv/bin/activate
```
Install dependencies on venv:
```
pip install -r requirements.txt
```
Create the database structure:
```
python manage.py migrate
```
Start the develompment server:
```
python manage.py runserver
```
The development server will be hosted at localhost:8000

## Authentication
Authentication credentials must be provided at /api/login/. This will return a JWT access and refresh token, 
the access token must be provided in the Authorization header as Bearer {access}.

For development purposes the default user is admin with password admin.

## Top Level Description
### Models
This project uses 4 basic models:
 - User: User model provided in the Django framework
 - Profile: User extension to store specific information. Links a user to accounts he has access.
 - Account: Holds a certain balance in a specific currency.
 - Transfer: Represents an exchange of a certain balance between accounts of the same currency.

### Users
Two types of users where implemented:
 - Admin: Has the is_staff flag on. Has full access to the backend.
 - User: Has access to its accounts, he can only create transfers and return transfers that he received.
 
### Implemented APIs
Four Apis where implemented:
 - User: Allows an admin to view, create, edit and delete users.
 - Profile: Allows an admin to view and edit a user profile.
 - Accounts: Allows an admin to view, create, edit and delete accounts. Allows a user to view his accounts.
 - Transfers: Allows an admin and a user to view, create and delete transfers.

### Admin panel

Admin user can access an administration panel at localhost:8000/admin to manage user creation and accounts with a simple GUI.

### Considerations

 - Users can have many accounts listed in their profile.
 - Admins have full access to all models.
 - No balance conciliation was implemented for edits to account balances.
 - No advanced database protection was used.
 - All secrets are provided on the code to make a simpler development, a .env should be used to distribute secrets in a real project.
  
## Project structure
### almaFintech
Alma fintech is the root of the project, contains the django settings and routing information.

### Login
This django app handles all user logic. 

| Path | Method | Action|
|------|--------|-------|
| /api/login/ | POST | Obtain token pair |
| /api/login/refresh/ | POST | Refresh token |
| /api/users/ | GET | List |
| /api/users/ | POST | Create |
| /api/users/{id}/ | GET | Retrieve |
| /api/users/{id}/ | POST | Edit |
| /api/users/{id}/ | PATCH | Partial Edit |
| /api/users/{id}/ | DELETE | Destroy |
| /api/profiles/ | GET | List |
| /api/profiles/{user_id}/ | GET | Retrieve |
| /api/profiles/{user_id}/ | POST | Edit |
| /api/profiles/{user_id}/ | PATCH | Partial Edit |
| /api/profiles/{user_id}/add_account/ | POST | Add account to user |
| /api/profiles/{user_id}/remove_account/ | POST | Remove account from user |

The profile model was defined to store additional information on users of the system.
```python
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
```

#### Permissions

Only admin user can create, edit or delete users and profiles. Users can view their profiles and their user model.


### Accounts
This django app handles all the logic corresponding to management of accounts and transfers between them. This uses the following apis endpoints:

| Path | Method | Action|
|------|--------|-------|
| /api/accounts/ | GET | List |
| /api/accounts/ | POST | Create |
| /api/accounts/{id}/ | GET | Retrieve |
| /api/accounts/{id}/ | POST | Edit |
| /api/accounts/{id}/ | PATCH | Partial Edit |
| /api/accounts/{id}/ | DELETE | Destroy |
| /api/accounts/{id}/transfers/ | GET | List account transfers |
| /api/accounts/biggest/ | GET | List biggest account of each currency |
| /api/transfers/ | GET | List |
| /api/transfers/ | POST | Create |
| /api/transfers/{id}/ | GET | Retrieve |
| /api/accounts/{id}/ | DELETE | Destroy |


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


```
The transfer model was extended in functionality to modify the accounts upon creation and when its cancelled.

This models get stored in an sql database of choice, for this demo the default sqlite3 database is used.


#### serializers.py
This file handles the serialization of the Account and Transfer model.

#### views.py
Views implement the view logic for each model. This uses a standard uri tree following this structure:

| Path | Method | Action|
|------|--------|-------|
| / | GET | List |
| / | POST | Create |
| /{id} | GET | Retrieve |
| /{id} | POST | Edit |
| /{id} | PATCH | Partial Edit |
| /{id} | DELETE | Destroy |
| /{id}/{extra} | {method} | Custom Detail Action |
| /{extra} | {method} | Custom Action |

For accounts viewset the extra actions transfers lists all transfers for a specific account and biggest returns the biggest account of each currency.
  

```python
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, AccountPermissions]

    def get_queryset(self):
        user = self.request.user
        # If user is staff of the virtual wallet return all Accounts
        if user.is_staff:
            return Account.objects.all()
        # If user is not staff only return its accounts
        return user.profile.accounts.all()

    @action(methods=['get'], detail=True)
    def transfers(self, request, id=None):
        transfers = Transfer.objects.filter(Q(origin_id=id) | Q(destination_id=id))
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def biggest(self, request):
        # Annotate biggest account by currency
        accounts = self.get_queryset().values('currency').annotate(max_balance=Max('balance')).order_by()
        if accounts.exists():
            # Create query for account matching biggest balance and currency
            q_statement = Q()
            for pair in accounts:
                q_statement |= (Q(currency__exact=pair['currency']) & Q(balance=pair['max_balance']))
            # Return biggest account of each currency
            model_set = self.get_queryset().filter(q_statement)
            serializer = AccountSerializer(model_set, many=True)
            return Response(serializer.data)
        return Response({})


class TransfersViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = TransferSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, TransferPermissions]

    def get_queryset(self):
        user = self.request.user
        # If user is staff of the virtual wallet return all Accounts
        if user.is_staff:
            return Transfer.objects.all()
        # If user is not staff only return its accounts
        return Transfer.objects.filter(origin__in=user.profile.accounts.all())

```
#### permissions
The permissions for this views where defined are defined between permisssions.py, the queryset of the viewset and the model itself.

 - Admin has full access.
 - User can only access accounts listed in his profile.
 - User cant edit, create or destroy accounts.
 - Transfers cant be modified.
 - Transfers must be to and from accounts of the same currency.
 - Transfers can only be reverted from a receiving account.
