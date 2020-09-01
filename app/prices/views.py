from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet

from prices.models import CarPrice
from prices.serializers import CarPriceSerializer


class CarPriceViewSet(ModelViewSet):
    queryset = CarPrice.objects.all()
    serializer_class = CarPriceSerializer
