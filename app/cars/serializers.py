from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car


class CarSerializer(ModelSerializer):
    class Meta:
        model = Car
        fields = ['id',
                  'number',
                  'name',
                  'zone',
                  'image',
                  'manufacturer',
                  'fuel',
                  'type',
                  'shift_type',
                  'riding_capacity',
                  'is_event_model',
                  'manual_page',
                  'safety_option',
                  'convenience_option'
                  ]
        read_only_fields = ['id',
                            'number',
                            'name',
                            'zone',
                            'image',
                            'manufacturer',
                            'fuel',
                            'type',
                            'shift_type',
                            'riding_capacity',
                            'is_event_model',
                            'manual_page',
                            'safety_option',
                            'convenience_option'
                            ]


class SummaryCarSerializer(ModelSerializer):
    # price 부분을 시간 계산된 값으로 바꿔야 함
    price = serializers.IntegerField(source='car_prices.standard_price')

    class Meta:
        model = Car
        fields = ['id', 'name', 'image', 'price', ]
        read_only_fields = ['id', 'name', 'image', 'price', ]
