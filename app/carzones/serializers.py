from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.serializers import CarTimeTableSerializer
from prices.serializers import SummaryCarAndCarPriceSerializer
from .models import CarZone


class CarZoneSerializer(ModelSerializer):
    class Meta:
        model = CarZone
        fields = ['id',
                  'name',
                  'address',
                  'region',
                  'latitude',
                  'longitude',
                  'image',
                  'sub_info',
                  'detail_info',
                  'type',
                  'operating_time']
        read_only_fields = ['id',
                            'name',
                            'address',
                            'region',
                            'latitude',
                            'longitude',
                            'image',
                            'sub_info',
                            'detail_info',
                            'type',
                            'operating_time']


class CarZonePricesSerializer(ModelSerializer):
    cars = SummaryCarAndCarPriceSerializer(many=True, read_only=True)
    time_tables = CarTimeTableSerializer(many=True, read_only=True)

    class Meta:
        model = CarZone
        fields = ['id', 'name', 'sub_info', 'type', 'cars', 'time_tables']
        read_only_fields = ['id', 'name', 'sub_info', 'type', 'cars', 'time_tables']


