from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

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


class SummaryCarZoneSerializer(ModelSerializer):
    class Meta:
        model = CarZone
        fields = ['id', 'name', 'sub_info', 'type']
        read_only_fields = ['id', 'name', 'sub_info', 'type']


class CarZonePricesSerializer(ModelSerializer):
    carzone = SummaryCarZoneSerializer(read_only=True)
    cars = SummaryCarAndCarPriceSerializer(many=True, read_only=True)

    class Meta:
        model = CarZone
        fields = ['carzone', 'cars']
        read_only_fields = ['carzone', 'cars']

    def validate(self, attrs):
        print('hello')
        print(attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        print('me?')
        return super().create(validated_data)


