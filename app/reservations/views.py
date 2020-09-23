from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from carzones.models import CarZone
from core.utils import insurance_price, time_format
from core.exceptions import (
    ReservationDoesNotExistException, CarZoneDoesNotExistException, CarDoesNotExistException,
    TooLessOrTooMuchTimeException, BeforeTheCurrentTimeException

)
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer, ReservationInsuranceUpdateSerializer, ReservationTimeUpdateSerializer,
    CarReservedTimesSerializer, CarzoneAvailableCarsSerializer, ReservationSerializer,
    ReservationTimeExtensionUpdateSerializer, AddressSerializer
)


class CarzoneRetrieveViews(RetrieveAPIView):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise CarZoneDoesNotExistException


class CarzoneAvailableCarsViews(RetrieveAPIView):
    serializer_class = CarzoneAvailableCarsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            time_from = time_format(self.request.data['from_when'])
            time_to = time_format(self.request.data['to_when'])

            MIN_DURATION = 30 * 60
            MAX_DURATION = 30 * 60 * 24 * 60

            if not MIN_DURATION <= (time_to - time_from).total_seconds() <= MAX_DURATION:
                raise TooLessOrTooMuchTimeException

            if time_from <= timezone.now():
                raise BeforeTheCurrentTimeException

            carzone = CarZone.objects.get(pk=self.kwargs['carzone_id'])
            return carzone
        except ObjectDoesNotExist:
            raise CarZoneDoesNotExistException

    def get_serializer_context(self):
        return {
            'time_from': time_format(self.request.data['from_when']),
            'time_to': time_format(self.request.data['to_when'])
        }


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


class ReservationRetrieveViews(RetrieveAPIView):
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Reservation.objects.get(pk=self.kwargs['reservation_id'])
            return reservation
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException


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
        from_when = reservation.from_when
        to_when = reservation.to_when

        return Response({
            'special': insurance_price('special', from_when, to_when),
            'standard': insurance_price('standard', from_when, to_when),
            'light': insurance_price('light', from_when, to_when)
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
