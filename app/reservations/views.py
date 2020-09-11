import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from cars.models import Car
from carzones.models import CarZone
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer, ReservationInsuranceUpdateSerializer, ReservationTimeUpdateSerializer,
    CarReservedTimesSerializer, CarzoneAvailableCarsSerializer, CarsSerializer, ReservationCarUpdateSerializer
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


class ReservationCarzoneAvailableCarsViews(generics.ListAPIView):
    serializer_class = CarsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        try:
            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            cars = carzone.cars.exclude(reservations=reservation).exclude(reservations__is_finished=True).exclude(
                reservations__from_when__lte=reservation.to_when,
                reservations__to_when__gte=reservation.to_when
            ).exclude(
                reservations__from_when__lte=reservation.from_when,
                reservations__to_when__gte=reservation.from_when
            ).exclude(
                reservations__from_when__gte=reservation.from_when,
                reservations__to_when__lte=reservation.to_when
            )
            return cars
        except ObjectDoesNotExist:
            raise ValueError('해당하는 carzone 혹은 reservation 인스턴스가 존재하지 않습니다.')

    def get_serializer_context(self):
        reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
        return {
            'from_when': reservation.from_when,
            'to_when': reservation.to_when
        }


class ReservationCarUpdateViews(generics.UpdateAPIView):
    serializer_class = ReservationCarUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ValueError('해당하는 reservation 인스턴스가 존재하지 않습니다.')

    def get_serializer_context(self):
        carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
        reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)

        cars = carzone.cars.exclude(reservations=reservation).exclude(reservations__is_finished=True).exclude(
            reservations__from_when__lte=reservation.to_when,
            reservations__to_when__gte=reservation.to_when
        ).exclude(
            reservations__from_when__lte=reservation.from_when,
            reservations__to_when__gte=reservation.from_when
        ).exclude(
            reservations__from_when__gte=reservation.from_when,
            reservations__to_when__lte=reservation.to_when
        )
        return {
            'cars': cars
        }


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
            from_when = datetime.datetime.strptime(self.request.data['from_when'], '%Y-%m-%dT%H:%M:%S.%f')
            to_when = datetime.datetime.strptime(self.request.data['to_when'], '%Y-%m-%dT%H:%M:%S.%f')

            if not (30 * 60 <= (to_when - from_when).total_seconds() <= 30 * 60 * 24 * 60):
                raise ValueError('최소 30분부터 최대 30일까지 설정 가능합니다.')

            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise ValueError('해당하는 carzone 인스턴스가 존재하지 않습니다.')

    def get_serializer_context(self):
        return {
            'to_when': self.request.data['to_when'],
            'from_when': self.request.data['from_when']
        }
