from rest_framework.serializers import ModelSerializer

from .models import CarZone


class CarZoneSerializer(ModelSerializer):
    class Meta:
        model = 'carzones.CarZone'
        fields = ['id',
                  'zone_id',
                  'name',
                  'address',
                  'region',
                  'latitude',
                  'longitude',
                  'detail_info',
                  'blog_page',
                  'type']
        read_only_fields = ['id',
                            'zone_id',
                            'name',
                            'address',
                            'region',
                            'latitude',
                            'longitude',
                            'detail_info',
                            'blog_page',
                            'type']

