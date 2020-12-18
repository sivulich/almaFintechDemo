from django.db.models import F
from rest_framework import serializers
from .models import Account, Transfer


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'currency', 'balance']
        lookup_field = 'id'


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'origin', 'destination', 'balance', 'cancelled']
        lookup_field = 'id'



