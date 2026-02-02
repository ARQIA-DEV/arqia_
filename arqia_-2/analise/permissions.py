from rest_framework.permissions import BasePermission


class IsAuthenticatedOrOptions(BasePermission):
    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True
        return bool(request.user and request.user.is_authenticated)
