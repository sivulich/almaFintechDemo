from django.db.models import Q, Max
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Account, Transfer
from .serializers import AccountSerializer, TransferSerializer
from .permissions import AccountPermissions, TransferPermissions


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
