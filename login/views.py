from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import UserPermissions, ProfilePermissions
from .serializers import UserSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets, mixins
from django.contrib.auth.models import User
from .models import Profile


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, UserPermissions]

    def get_queryset(self):
        user = self.request.user
        # If user is staff of the virtual wallet return all Accounts
        if user.is_staff:
            return User.objects.all()
        # If user is not staff only return its accounts
        return User.objects.filter(id=user.id)

    @action(methods=['get'], detail=True)
    def profile(self, request, id=None):
        profile = Profile.objects.get(user_id=id)
        return Response(ProfileSerializer(profile).data)


class ProfileViewSet(mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    lookup_field = 'user_id'
    permission_classes = [IsAuthenticated, ProfilePermissions]

    def get_queryset(self):
        user = self.request.user
        # If user is staff of the virtual wallet return all Accounts
        if user.is_staff:
            return Profile.objects.all()
        # If user is not staff only return its accounts
        return Profile.objects.filter(user_id=user.id)

    @action(methods=['post'], detail=True)
    def add_account(self, request, user_id=None):
        profile = Profile.objects.get(user_id=user_id)
        profile.accounts.add(request.data['account_id'])
        return Response(ProfileSerializer(profile).data)

    @action(methods=['post'], detail=True)
    def remove_account(self, request, user_id=None):
        profile = Profile.objects.get(user_id=user_id)
        profile.accounts.remove(request.data['account_id'])
        return Response(ProfileSerializer(profile).data)
