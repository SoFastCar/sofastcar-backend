from django.shortcuts import render

# Create your views here.
from requests import Response
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from prices.models import CarPrice
from prices.serializers import CarPriceSerializer


class CarPriceViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = CarPrice.objects.all()
    serializer_class = CarPriceSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        # ios 요청 : /carzones/123/cars/4/prices
        queryset = super().get_queryset()
        queryset = queryset.filter(car_id=self.kwargs.get('car_pk'))
        return queryset


