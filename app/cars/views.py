# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from cars.models import Car, PhotoBeforeUse
from cars.serializers import CarSerializer, PhotoBeforeUseSerializer
from core.permissions import IsOwner


class CarViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(zone=self.kwargs.get('carzone_pk'))
        return super().filter_queryset(queryset)


class PhotoBeforeUseViewSet(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            GenericViewSet):
    queryset = PhotoBeforeUse.objects.all()
    serializer_class = PhotoBeforeUseSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)

