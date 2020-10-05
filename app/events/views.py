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
    """
        SoFastCar App의 광고 이미지를 보여주는 API
        ---
        # 내용
            [GET] /event_photos
            -> 광고 이미지 리스트 반환
            [GET] /event_photos/123
            -> 특정 광고 이미지 반환
    """
    queryset = EventPhoto.objects.all()
    serializer_class = EventPhotoListSerializer
    permission_classes = [IsAuthenticated, ]
