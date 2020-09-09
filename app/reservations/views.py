from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer, ReservationInsuranceUpdateSerializer
)


class ReservationCreateViews(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)


class ReservationInsuranceUpdateViews(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationInsuranceUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['pk'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ValueError('해당하는 reservation 인스턴스가 존재하지 않습니다.')
