from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwner
from payments.models import PaymentBeforeUse, PaymentAfterUse
from payments.serializers import PaymentBeforeUseSerializer, PaymentAfterUseSerializer
from reservations.models import Reservation


class PaymentBeforeUseViewSet(mixins.ListModelMixin,
                              GenericViewSet):
    """
        [결제완료시] (지불 완료된)운행 전 요금 보기
        ---
        # 내용
            [GET] /reservations/5/payment_before : 특정 예약건에 대한 운행 전 요금 보기
    """
    queryset = PaymentBeforeUse.objects.all()
    serializer_class = PaymentBeforeUseSerializer
    permission_classes = [IsOwner, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(member=self.request.user, reservation_id=self.kwargs.get('reservation_pk'))
        return super().filter_queryset(queryset)


class PaymentAfterUseViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    """
        [반납시] 운행 거리에 따른 2차 결제
        ---
        # 내용
            [GET] /reservations/5/payment_after : 특정 예약건에 대한 운행 종료 후 2차 요금 보기
        ---
            [POST] /reservations/5/payment_after : 특정 예약건에 대한 반납 후 2차 요금 결제
            (운행종료 후 주차 체크 이후 반납하기 버튼 눌러서 결제되는 순간)
    """
    queryset = PaymentAfterUse.objects.all()
    serializer_class = PaymentAfterUseSerializer
    permission_classes = [IsOwner, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(member=self.request.user, reservation_id=self.kwargs.get('reservation_pk'))
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        get_object_or_404(Reservation, id=self.kwargs.get('reservation_pk'))
        serializer.save(member=self.request.user,
                        reservation_id=self.kwargs.get('reservation_pk'))

    def list(self, request, *args, **kwargs):
        get_object_or_404(Reservation, id=self.kwargs.get('reservation_pk'))
        get_object_or_404(PaymentAfterUse, reservation_id=self.kwargs.get('reservation_pk'))
        return super().list(request, *args, **kwargs)
