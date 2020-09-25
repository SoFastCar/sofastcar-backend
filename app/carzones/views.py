# Create your views here.
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from cars.models import Car
from core.utils import time_format
from .models import CarZone
from .serializers import CarZoneSerializer, CarZonePricesSerializer


class CarZoneViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = CarZone.objects.all()
    serializer_class = CarZoneSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == 'info':
            return CarZonePricesSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = CarZone.objects.filter(Q(address__icontains=keyword) | Q(name__icontains=keyword))
        return queryset

    @action(detail=False)
    def distance(self, request, *args, **kwargs):
        lat_per_km = 1 / 109.958489129649955
        lon_per_km = 1 / 88.74

        try:
            std_lat = float(request.query_params.get('lat'))
            std_lon = float(request.query_params.get('lon'))
            distance = float(request.query_params.get('distance'))
        except Exception as e:
            return Response('lat=float, lon=float, distance=float are required',
                            status=status.HTTP_400_BAD_REQUEST)

        boundary = {
            'max_lat': std_lat + lat_per_km * distance,
            'min_lat': std_lat - lat_per_km * distance,
            'max_lon': std_lon + lon_per_km * distance,
            'min_lon': std_lon - lon_per_km * distance,
        }
        zones = CarZone.objects.filter(latitude__gte=boundary['min_lat'],
                                       latitude__lte=boundary['max_lat'],
                                       longitude__gte=boundary['min_lon'],
                                       longitude__lte=boundary['max_lon'], )

        serializer = self.get_serializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def info(self, request, *args, **kwargs):
        carzone = get_object_or_404(CarZone, id=kwargs.get('pk'))
        try:
            date_time_start = request.query_params.get('date_time_start')
            date_time_end = request.query_params.get('date_time_end')
        except Exception as e:
            return Response('wrong date_time_format : ex)202009051430',
                            status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
