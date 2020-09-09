from rest_framework.serializers import ModelSerializer

from cars.serializers import SummaryCarSerializer
from .models import CarZone


class CarZoneSerializer(ModelSerializer):
    class Meta:
        model = CarZone
        fields = ['id',
                  'zone_id',
                  'name',
                  'address',
                  'region',
                  'latitude',
                  'longitude',
                  'sub_info',
                  'detail_info',
                  'type',
                  'operating_time']
        read_only_fields = ['id',
                            'zone_id',
                            'name',
                            'address',
                            'region',
                            'latitude',
                            'longitude',
                            'sub_info',
                            'detail_info',
                            'type',
                            'operating_time']


class SummaryCarZoneSerializer(ModelSerializer):
    cars = SummaryCarSerializer(many=True, read_only=True)

    class Meta:
        model = CarZone
        fields = ['id', 'name', 'type', 'sub_info', 'cars', ]
        read_only_fields = ['id', 'name', 'type', 'sub_info', 'cars', ]
