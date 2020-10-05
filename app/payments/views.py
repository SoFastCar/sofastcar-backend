from django.shortcuts import render


# Create your views here.
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwner
from payments.models import PaymentBeforeUse
from payments.serializers import PaymentBeforeUseSerializer


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