from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsB2BBuyer(BasePermission):
    """Only B2B buyers can create/update their own inquiries."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "buyer"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsB2BAdmin(BasePermission):
    """Only B2B admins can reply/delete inquiries."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "admin"
