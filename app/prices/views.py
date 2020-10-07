from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsOwner
from prices.models import Coupon
from prices.serializers import CouponSerializer


class CouponViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsOwner, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(member_id=self.kwargs.get('member_pk'))
        return super().filter_queryset(queryset)

    @action(detail=True)
    def use(self, request, *args, **kwargs):
        """
            특정 쿠폰을 사용하는 API
            ---
            # 내용
            [POST] /members/123/coupon/456/use
             -> 특정 쿠폰에 사용 체크하여 결제시 반영되도록 합니다.
        """
        instance = self.get_object()
        instance.will_use_check = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
