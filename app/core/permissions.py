from rest_framework import permissions


class IsUserSelf(permissions.BasePermission):
    """
    토큰을 가지고 자기 자신만 접속 가능
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAnonymous(permissions.BasePermission):
    """
    토큰을 가지고 있지 않아도 접근 가능
    """

    def has_permission(self, request, view):
        return request.user.is_anonymous


class IsOwner(permissions.BasePermission):
    """
    토큰을 가지고 자기 자신의 것만 접속 가능
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.member == request.user
