from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from carzones.models import CarZone
from core.permissions import IsOwner
from reservations.models import Reservation, PhotoBeforeUse
from reservations.serializers import ReservationSerializer, ReservationHistorySerializer, UseHistoryListSerializer, \
    PhotoBeforeUseSerializer


class ReservationViewSet(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    """
        [예약완료하기 버튼] 예약 생성 API

            [POST] /carzones/260/cars/1/reservations

            insurance : 'light' , 'standard', 'special' 중 택일
            date_time_start / end : iso format 반드시 UTC 기준으로 주셔야 합니다 !
        ---
            예시) "2020-10-12T04:00:00Z" 혹은 "2020-10-12T04:00:00+00:00"
            -> response시 받는 형태는 "2020-10-12T04:00:00Z" 형태입니다 ('00Z':UTC기준)
            -> "%Y-%m-%dT%H%M%z" (%z : +0000 형태인데 response시 현재 00Z 형태로만 나옵니다..)
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsOwner, ]

    def perform_create(self, serializer):
        get_object_or_404(CarZone, id=self.kwargs.get('carzone_pk'))
        get_object_or_404(Car, id=self.kwargs.get('car_pk'))
        serializer.save(member=self.request.user,
                        zone_id=self.kwargs.get('carzone_pk'),
                        car_id=self.kwargs.get('car_pk'))


class ReservationHistoryViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    """
        생성된 예약 반환하는 API
        ---
        # 내용
            [GET] /reservations/123 : 요청한 사용자의 특정 예약 보기
            [GET] /reservations : 요청한 사용자의 예약 리스트 보기
            [GET] /reservations/history : 요청한 사용자의 이용 내역 리스트 보기
        ---
            DB 저장시 : UTC 기준으로 저장됩니다. (서버 시간은 현재 UTC 기준입니다.)
            예약 데이터를 볼때 Response : KST(한국시간) 기준으로 보입니다.
            created_at, updated_at : DB 저장시간 기록용 값입니다
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationHistorySerializer
    permission_classes = [IsOwner, ]

    def get_serializer_class(self):
        if self.action == 'history':
            return UseHistoryListSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        queryset = queryset.filter(member=self.request.user)
        return super().filter_queryset(queryset)

    @action(detail=False)
    def history(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PhotoBeforeUseViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    """
        차량 탑승전 사진 업로드 및 보여주기 위한 API
        ---
        # 내용
        [POST] /reservations/123/photos
            -> 해당 예약건에 대한 탑승전 사진 업로드(이미지 다중 업로드 가능)
        [GET] /reservations/123/photos
            -> 해당 예약건에 대한 탑승전 사진 리스트 보기
    """
    queryset = PhotoBeforeUse.objects.all()
    serializer_class = PhotoBeforeUseSerializer
    permission_classes = [IsOwner, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(reservation_id=self.kwargs.get('reservation_pk'))
        return queryset

    def perform_create(self, serializer):
        reservation = get_object_or_404(Reservation, id=self.kwargs.get('reservation_pk'))
        serializer.save(member=self.request.user, reservation=reservation)
