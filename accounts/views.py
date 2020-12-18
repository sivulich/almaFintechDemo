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
        transfers = Transfer.objects.filter(origin_id=id)
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)


class TransfersViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
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






