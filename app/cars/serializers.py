from django.db.models import Q
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car, CarTimeTable
from core.utils import KST, time_format, get_only_date_from_datetime, get_only_date_end_from_datetime
from prices.serializers import CarPriceDetailSerializer


class FilteredTimeTableListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        # trans str KST to datetime aware UTC format start-00:00:00 ~ end-23:59:59
        date_start = get_only_date_from_datetime(
            time_format(self.context.get('request').query_params.get('date_time_start')))
        date_end = get_only_date_end_from_datetime(time_format(self.context.get('request').query_params.get('date_time_end')))
        data = data.filter(date_time_start__gte=date_start, date_time_start__lte=date_end)
        return super(FilteredTimeTableListSerializer, self).to_representation(data)


class CarTimeTableSerializer(ModelSerializer):
    # response : car_pk에 해당하는 시간표 한국시간대로 표기
    date_time_start = serializers.DateTimeField(read_only=True, default_timezone=KST)
    date_time_end = serializers.DateTimeField(read_only=True, default_timezone=KST)

    class Meta:
        list_serializer_class = FilteredTimeTableListSerializer
        model = CarTimeTable
        fields = ['id', 'zone', 'car', 'date_time_start', 'date_time_end']
        read_only_fields = ['id', 'zone', 'car']


class CarSerializer(ModelSerializer):
    car_prices = CarPriceDetailSerializer(read_only=True, source='carprice')
    term_price = serializers.SerializerMethodField()
    insurance_prices = serializers.SerializerMethodField()
    time_tables = CarTimeTableSerializer(read_only=True, many=True)

    class Meta:
        model = Car
        fields = ['id',
                  'number',
                  'name',
                  'zone',
                  'image',
                  'manufacturer',
                  'fuel_type',
                  'type_of_vehicle',
                  'shift_type',
                  'riding_capacity',
                  'is_event_model',
                  'manual_page',
                  'safety_option',
                  'convenience_option',
                  'car_prices',
                  'term_price',
                  'insurance_prices',
                  'time_tables'
                  ]
        read_only_fields = ['id',
                            'number',
                            'name',
                            'zone',
                            'image',
                            'manufacturer',
                            'fuel_type',
                            'type_of_vehicle',
                            'shift_type',
                            'riding_capacity',
                            'is_event_model',
                            'manual_page',
                            'safety_option',
                            'convenience_option',
                            'car_prices',
                            'term_price',
                            'insurance_prices',
                            'time_tables'
                            ]

    def get_term_price(self, car):
        date_time_start = self.context.get('request').query_params.get('date_time_start')
        date_time_end = self.context.get('request').query_params.get('date_time_end')
        return car.carprice.get_price(date_time_start, date_time_end)

    def get_insurance_prices(self, car):
        date_time_start = self.context.get('request').query_params.get('date_time_start')
        date_time_end = self.context.get('request').query_params.get('date_time_end')
        return {
            'special': car.insurances.get_special_price(date_time_start, date_time_end),
            'standard': car.insurances.get_standard_price(date_time_start, date_time_end),
            'light': car.insurances.get_light_price(date_time_start, date_time_end)
        }


class CarDetailInfoSerializer(ModelSerializer):
    car_prices = CarPriceDetailSerializer(read_only=True, source='carprice')
    class Meta:
        model = Car
        fields = ['id',
                  'number',
                  'name',
                  'zone',
                  'image',
                  'manufacturer',
                  'fuel_type',
                  'type_of_vehicle',
                  'shift_type',
                  'riding_capacity',
                  'is_event_model',
                  'manual_page',
                  'safety_option',
                  'convenience_option',
                  'car_prices'
                  ]
        read_only_fields = ['id',
                            'number',
                            'name',
                            'zone',
                            'image',
                            'manufacturer',
                            'fuel_type',
                            'type_of_vehicle',
                            'shift_type',
                            'riding_capacity',
                            'is_event_model',
                            'manual_page',
                            'safety_option',
                            'convenience_option',
                            'car_prices'
                            ]
