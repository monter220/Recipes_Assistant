from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Правки может вносить автор, смотреть - все."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)
