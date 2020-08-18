from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from members.serializers import MembersSerializer


class MembersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = MembersSerializer
