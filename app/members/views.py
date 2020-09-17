from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from members.models import Member, Profile, PhoneAuth
from core.permissions import IsOwner, IsAnonymous
from members.serializers import MembersSerializer, ChangePasswordSerializer, ProfileSerializer, PhoneAuthSerializer, \
    CheckAuthNumberSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet


class MembersViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MembersSerializer

    permission_class = [IsAnonymous]

    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        else:
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'change_password':
            return [IsOwner()]
        return super().get_permissions()

    @action(methods=['put'], detail=True)
    def change_password(self, request, *args, **kwargs):
        """
        사용자 비밀번호 변경
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.password = request.data['change_password']
        request.user.save()

        return Response(status=status.HTTP_200_OK)


class ProfileViewSet(mixins.ListModelMixin,
                     GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def filter_queryset(self, queryset):
        if self.action == 'list':
            queryset = queryset.filter(member=self.request.user)
        return super().filter_queryset(queryset)


class PhoneAuthViewSet(ModelViewSet):
    queryset = PhoneAuth.objects.all()
    serializer_class = PhoneAuthSerializer

    def get_serializer_class(self):
        if self.action == 'check_auth_number':
            return CheckAuthNumberSerializer
        else:
            return super().get_serializer_class()

    @action(methods=['put'], detail=True)
    def check_auth_number(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if int(instance.auth_number) == int(request.data['check_auth_number']):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
