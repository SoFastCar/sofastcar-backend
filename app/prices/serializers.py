from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car
from core.utils import time_format
from prices.models import CarPrice, InsuranceFee


class CarPriceDetailSerializer(ModelSerializer):
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


class SummaryCarAndCarPriceSerializer(ModelSerializer):
    term_price = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ['id', 'name', 'image', 'is_event_model', 'term_price']
        read_only_fields = ['id', 'name', 'image', 'is_event_model', 'term_price']

    def get_term_price(self, car):
        date_time_start = self.context.get('request').query_params.get('date_time_start')
        date_time_end = self.context.get('request').query_params.get('date_time_end')
        return car.carprice.get_price(date_time_start, date_time_end)


class InsuranceFeeSerializer(ModelSerializer):
    insurance_prices = serializers.SerializerMethodField()

    class Meta:
        model = InsuranceFee
        fields = ['id', 'car', 'insurance_prices']
        read_only_fields = ['id', 'car', 'insurance_prices']

    def get_insurance_price(self, car):
        date_time_start = self.context.get('date_time_start')
        date_time_end = self.context.get('date_time_end')
        return {
            'special': car.insurance_fees.insurance_rantal_price(date_time_start, date_time_end),
            'standard': car.insurance_fees.insurance_rantal_price(date_time_start, date_time_end),
            'light': car.insurance_fees.insurance_rantal_price(date_time_start, date_time_end),
        }