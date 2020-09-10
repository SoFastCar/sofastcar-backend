from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car, PhotoBeforeUse


class CarSerializer(ModelSerializer):
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
                  'convenience_option'
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
                            'convenience_option'
                            ]


class SummaryCarSerializer(ModelSerializer):
    # price 부분을 시간 계산된 값으로 바꿔야 함
    price = serializers.IntegerField(source='car_prices.standard_price')

    class Meta:
        model = Car
        fields = ['id', 'name', 'image', 'price', ]
        read_only_fields = ['id', 'name', 'image', 'price', ]


class PhotoBeforeUseSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = PhotoBeforeUse
        fields = ['id', 'member', 'image', 'photos']
        read_only_fields = ('id', 'member', 'image')

    def create(self, validated_data):
        # reservation = Reservation.objects.get(id=self.context['request'].data['reservation_id'])
        images_data = self.context['request'].FILES
        photo_bulk_list = []

        for image in images_data.getlist('photos'):
            photo = PhotoBeforeUse(
                # reservation=reservation,
                image=image,
                member=self.context['request'].user)
            photo_bulk_list.append(photo)
        instance = PhotoBeforeUse.objects.bulk_create(photo_bulk_list)

        return instance
