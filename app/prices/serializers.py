from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from prices.models import CarPrice


class CarPriceSerializer(ModelSerializer):
    class Meta:
        model = CarPrice
        fields = ['id',
                  'car',
                  'standard_price',
                  'min_price_per_km',
                  'mid_price_per_km',
                  'max_price_per_km'
                  ]
        read_only_fields = ['id',
                            'car',
                            'standard_price',
                            'min_price_per_km',
                            'mid_price_per_km',
                            'max_price_per_km'
                            ]
