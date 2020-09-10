from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from cars.models import Car
from carzones.models import CarZone
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer, ReservationInsuranceUpdateSerializer, ReservationTimeUpdateSerializer,
    CarReservedTimesSerializer, CarzoneAvailableCarsSerializer, CarzoneDetailSerializer
)


class ReservationCreateViews(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)


class ReservationInsuranceUpdateViews(generics.UpdateAPIView):
    serializer_class = ReservationInsuranceUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ValueError('해당하는 reservation 인스턴스가 존재하지 않습니다.')


class ReservationTimeUpdateViews(generics.UpdateAPIView):
    serializer_class = ReservationTimeUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ValueError('해당하는 reservation 인스턴스가 존재하지 않습니다.')


class CarReservedTimesViews(generics.ListAPIView):
    serializer_class = CarReservedTimesSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        try:
            car = Car.objects.get(pk=self.kwargs['car_id'])
            reservations = Reservation.objects.filter(is_finished=False, car=car)
            return reservations
        except ObjectDoesNotExist:
            raise ValueError('해당하는 car 인스턴스가 존재하지 않습니다.')


class CarzoneAvailableCarsViews(generics.RetrieveAPIView):
    serializer_class = CarzoneAvailableCarsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise ValueError('해당하는 carzone 인스턴스가 존재하지 않습니다.')

    def get_serializer_context(self):
        return {
            'to_when': self.request.data['to_when'],
            'from_when': self.request.data['from_when']
        }


class CarzoneDetailViews(generics.RetrieveAPIView):
    queryset = CarZone.objects.all()
    serializer_class = CarzoneDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise ValueError('해당하는 carzone 인스턴스가 존재하지 않습니다.')
