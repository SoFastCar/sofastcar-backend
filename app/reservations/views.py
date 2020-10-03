from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from carzones.models import CarZone
from core.permissions import IsOwner
from reservations.models import Reservation
from reservations.serializers import ReservationSerializer


class ReservationViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsOwner, ]

    def perform_create(self, serializer):
        get_object_or_404(CarZone, id=self.kwargs.get('carzone_pk'))
        get_object_or_404(Car, id=self.kwargs.get('car_pk'))
        serializer.save(member=self.request.user,
                        zone_id=self.kwargs.get('carzone_pk'),
                        car_id=self.kwargs.get('car_pk'))


