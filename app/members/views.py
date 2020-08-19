from rest_framework import mixins
from members.models import Member
from rest_framework.viewsets import GenericViewSet
from members.serializers import MembersSerializer


class MembersViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    """Member """
    queryset = Member.objects.all()
    serializer_class = MembersSerializer
