from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car, PhotoBeforeUse
from reservations.models import Reservation


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


class PhotoBeforeUseSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = PhotoBeforeUse
        fields = ['id', 'member', 'reservation', 'image', 'photos']
        read_only_fields = ['id', 'member', 'reservation', 'image']

    def validate(self, attrs):
        # 예약 존재 여부 확인
        if Reservation.objects.filter(id=self.context['view'].kwargs['reservation_pk']).exists():
            instance = Reservation.objects.get(id=self.context['view'].kwargs['reservation_pk'])
            # 요청 유저가 예약한 유저인지 확인
            if instance.member == self.context['request'].user:
                return attrs
            else:
                raise serializers.ValidationError('Reservation member != request.user')
        else:
            raise serializers.ValidationError('Reservation does not exists')

    def create(self, validated_data):
        images_data = self.context['request'].FILES
        photo_bulk_list = []

        for image in images_data.getlist('photos'):
            photo = PhotoBeforeUse(
                reservation=validated_data.get('reservation'),
                image=image,
                member=self.context['request'].user)
            photo_bulk_list.append(photo)
        instance = PhotoBeforeUse.objects.bulk_create(photo_bulk_list)

        return instance
