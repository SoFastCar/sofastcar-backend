from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from events.models import EventPhoto
from events.serializers import EventPhotoListSerializer


class EventPhotoViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = EventPhoto.objects.all()
    serializer_class = EventPhotoListSerializer
    permission_classes = [IsAuthenticated, ]
