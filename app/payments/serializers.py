from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from payments.models import PaymentBeforeUse, PaymentAfterUse
from reservations.models import Reservation


class PaymentBeforeUseSerializer(ModelSerializer):
    class Meta:
        model = PaymentBeforeUse
        fields = ['id',
                  'member',
                  'reservation',
                  'rental_fee',
                  'insurance_fee',
                  'coupon_discount',
                  'etc_discount',
                  'extension_fee',
                  'total_fee',
                  'created_at',
                  'updated_at']
        read_only_fields = ['id',
                            'member',
                            'reservation',
                            'rental_fee',
                            'insurance_fee',
                            'coupon_discount',
                            'etc_discount',
                            'extension_fee',
                            'total_fee',
                            'created_at',
                            'updated_at']


class PaymentAfterUseSerializer(ModelSerializer):
    class Meta:
        model = PaymentAfterUse
        fields = ['id',
                  'member',
                  'reservation',
                  'driving_distance',
                  'first_section_fee',
                  'second_section_fee',
                  'third_section_fee',
                  'total_toll_fee',
                  'total_fee',
                  'created_at',
                  'updated_at'
                  ]
        read_only_fields = ['id',
                            'member',
                            'reservation',
                            'first_section_fee',
                            'second_section_fee',
                            'third_section_fee',
                            'total_toll_fee',
                            'total_fee',
                            'created_at',
                            'updated_at'
                            ]

    def validate(self, attrs):
        # 2차 결제 여부 체크
        if PaymentAfterUse.objects.filter(reservation_id=self.context['view'].kwargs.get('reservation_pk')).exists():
            raise serializers.ValidationError('해당 건은 이미 결제완료되었습니다.')

        return attrs

    def create(self, validated_data):

        distance = validated_data.get('driving_distance')
        reservation = Reservation.objects.get(id=validated_data.get('reservation_id'))

        # TollFee 계산 구간
        total_toll_fee = 0

        # 구간별 거리 계산
        if 100 < distance:
            first_section_fee = (distance - 100) * reservation.car.carprice.min_price_per_km
            second_section_fee = 70 * reservation.car.carprice.mid_price_per_km
            third_section_fee = 30 * reservation.car.carprice.max_price_per_km
        elif 30 < distance < 100:
            first_section_fee = 0
            second_section_fee = (distance - 70) * reservation.car.carprice.mid_price_per_km
            third_section_fee = 30 * reservation.car.carprice.max_price_per_km
        elif distance < 30:
            first_section_fee = 0
            second_section_fee = 0
            third_section_fee = distance * reservation.car.carprice.max_price_per_km

        total_fee = first_section_fee + second_section_fee + third_section_fee - total_toll_fee

        instance = PaymentAfterUse.objects.create(member=validated_data['member'],
                                                  driving_distance=distance,
                                                  reservation_id=validated_data['reservation_id'],
                                                  first_section_fee=first_section_fee,
                                                  second_section_fee=second_section_fee,
                                                  third_section_fee=third_section_fee,
                                                  total_toll_fee=total_toll_fee,
                                                  total_fee=total_fee)
        return instance

