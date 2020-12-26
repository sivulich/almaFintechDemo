from rest_framework import permissions


class ProfilePermissions(permissions.BasePermission):
    message = 'Customer can only view its profile.'

    # To list and create only admins
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # All users have view permissions for their profile
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins have all permissions
        return request.user.is_staff


class UserPermissions(permissions.BasePermission):
    message = 'Customer can only view its profile.'

    # To list and create only admins
    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # All users have view permissions for their profile
        if request.method in permissions.SAFE_METHODS and obj.id == request.user.id:
            return True

        # Admins have all permissions
        return request.user.is_staff
