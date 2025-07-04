from rest_framework import permissions

class IsAdminUserCustom(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role_connector.is_admin
        )
class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_admin = request.user.role_connector.is_admin
        is_self = obj.user == request.user
        return is_self or is_admin

# class IsAuthenticated
