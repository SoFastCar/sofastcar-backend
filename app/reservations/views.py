import datetime

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from carzones.models import CarZone
from core.utils import insurance_price
from core.exceptions import (
    ReservationDoesNotExistException, CarZoneDoesNotExistException, CarDoesNotExistException,
    TooLessOrTooMuchTimeException, BeforeTheCurrentTimeException
)
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer, ReservationInsuranceUpdateSerializer, ReservationTimeUpdateSerializer,
    CarReservedTimesSerializer, CarzoneAvailableCarsSerializer, CarsSerializer, ReservationCarUpdateSerializer,
    ReservationSerializer, ReservationTimeExtensionUpdateSerializer
)


class ReservationCreateViews(CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)

    def get_serializer_context(self):
        return {
            'member': self.request.user
        }


class ReservationInsurancePricesViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, reservation_id):
        try:
            reservation = Reservation.objects.get(pk=reservation_id, member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

    def get(self, request, reservation_id):
        reservation = self.get_object(reservation_id)
        return Response({
            'special': insurance_price('special', reservation.from_when, reservation.to_when),
            'standard': insurance_price('standard', reservation.from_when, reservation.to_when),
            'light': insurance_price('light', reservation.from_when, reservation.to_when)
        })


class ReservationInsuranceUpdateViews(UpdateAPIView):
    serializer_class = ReservationInsuranceUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

    def get_serializer_context(self):
        return {
            'reservation': Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
        }


class ReservationTimeUpdateViews(UpdateAPIView):
    serializer_class = ReservationTimeUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

    def get_serializer_context(self):
        return {
            'reservation': Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
        }


class ReservationCarzoneAvailableCarsViews(ListAPIView):
    serializer_class = CarsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        try:
            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            try:
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
                raise ReservationDoesNotExistException
        except ObjectDoesNotExist:
            raise CarZoneDoesNotExistException

    def get_serializer_context(self):
        reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
        return {
            'from_when': reservation.from_when,
            'to_when': reservation.to_when
        }


class ReservationCarUpdateViews(UpdateAPIView):
    serializer_class = ReservationCarUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'], member=self.request.user)
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

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
            'cars': cars,
            'reservation': reservation
        }


class CarReservedTimesViews(ListAPIView):
    serializer_class = CarReservedTimesSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        try:
            car = Car.objects.get(pk=self.kwargs['car_id'])
            reservations = Reservation.objects.filter(is_finished=False, car=car)
            return reservations
        except ObjectDoesNotExist:
            raise CarDoesNotExistException


class CarzoneAvailableCarsViews(RetrieveAPIView):
    serializer_class = CarzoneAvailableCarsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            from_when = datetime.datetime.strptime(self.request.data['from_when'], '%Y-%m-%dT%H:%M:%S.%f')
            to_when = datetime.datetime.strptime(self.request.data['to_when'], '%Y-%m-%dT%H:%M:%S.%f')

            if not (30 * 60 <= (to_when - from_when).total_seconds() <= 30 * 60 * 24 * 60):
                raise TooLessOrTooMuchTimeException

            if from_when <= datetime.datetime.now():
                raise BeforeTheCurrentTimeException

            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise CarZoneDoesNotExistException

    def get_serializer_context(self):
        return {
            'to_when': self.request.data['to_when'],
            'from_when': self.request.data['from_when']
        }


class ReservationViewSet(mixins.ListModelMixin,
                         GenericViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, ]

    def filter_queryset(self, queryset):
        # 요청한 유저의 예약건만 필터링
        if self.action == 'list':
            queryset = queryset.filter(member=self.request.user)
        return super().filter_queryset(queryset)


class ReservationTimeExtensionUpdateViews(UpdateAPIView):
    serializer_class = ReservationTimeExtensionUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'])
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

    def get_serializer_context(self):
        reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'])
        return {
            'reservation': reservation
        }
