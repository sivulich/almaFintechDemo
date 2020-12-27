from django.db.models import F
from rest_framework import serializers
from .models import Account, Transfer


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'currency', 'balance']
        lookup_field = 'id'


class TransferSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(read_only=True)
    currency = serializers.SerializerMethodField(read_only=True)

    def get_currency(self, obj):
        return obj.origin.currency

    class Meta:
        model = Transfer
        fields = ['id', 'date', 'origin', 'destination', 'currency', 'balance', 'cancelled']
        lookup_field = 'id'



