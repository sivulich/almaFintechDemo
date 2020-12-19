from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'cuit', 'phone', 'company', 'accounts']
        lookup_field = 'id'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'is_staff', 'is_active']
        lookup_field = 'id'

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        Profile.objects.create(user=user)
        return user


