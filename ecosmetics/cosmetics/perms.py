from rest_framework import permissions


class CanCommentOnProduct(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return True
        return False