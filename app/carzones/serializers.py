from rest_framework.serializers import ModelSerializer

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
