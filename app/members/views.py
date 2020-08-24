from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from members.models import Member
from core.permissions import IsOwner, IsAnonymous
from members.serializers import MembersSerializer, ChangePasswordSerializer
from rest_framework.viewsets import ModelViewSet


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
