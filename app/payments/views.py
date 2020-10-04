from django.shortcuts import render


# Create your views here.
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwner
from payments.models import PaymentBeforeUse
from payments.serializers import PaymentBeforeUseSerializer


class PaymentBeforeUseViewSet(mixins.ListModelMixin,
                              GenericViewSet):
    queryset = PaymentBeforeUse.objects.all()
    serializer_class = PaymentBeforeUseSerializer
    permission_classes = [IsOwner, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(member=self.request.user, reservation_id=self.kwargs.get('reservation_pk'))
        return super().filter_queryset(queryset)