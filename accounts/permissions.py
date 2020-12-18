from rest_framework import permissions


class AccountPermissions(permissions.BasePermission):
    message = 'Customer can only view account.'

    def has_permission(self, request, view):
        # All users have view permissions for their accounts
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class TransferPermissions(permissions.BasePermission):
    message = 'Customer can only create transfers for his account or cancel received transfers'

    def has_permission(self, request, view):
        # All users have view permissions for their accounts
        if request.method in permissions.SAFE_METHODS:
            return True

        # Is admin user
        if request.user.is_staff:
            return True

        # Allow user to create a transfer
        if request.method == 'POST':
            return request.user.profile.accounts.filter(id=request.data['origin']).exists()

        if request.method == 'DELETE':
            # Must check object level permissions
            return True
        # Default to false
        return False

    def has_object_permission(self, request, view, obj):
        # All users have view permissions for their accounts
        if request.method in permissions.SAFE_METHODS:
            return True

        # Is admin user
        if request.user.is_staff:
            return True

        # Allow users to return a transfer
        if request.method == 'DELETE':
            return request.user.profile.accounts.filter(id=obj.destination_id).exists()

        return False
