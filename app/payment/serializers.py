from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.exceptions import ReservationDoesNotExistException
from core.utils import payment_price, KST
from payment.models import Payment
from reservations.models import Reservation
from reservations.serializers import ReservationSerializer


class PaymentSerializer(serializers.ModelSerializer):
    distance_credit = serializers.IntegerField(source='miles_credit')
    payment_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    reservation = ReservationSerializer()

    class Meta:
        model = Payment
        fields = (
            'id',
            'distance',
            'distance_credit',
            'payment_date',
            'reservation',
        )


class PaymentCreateSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    distance = serializers.FloatField()

    def validate(self, attrs):
        try:
            # reservation 인스턴스 확인
            reservation = Reservation.objects.get(pk=attrs['reservation_id'])
            if reservation.payment or reservation.is_finished:
                raise serializers.ValidationError('이미 반납 결제된 예약 인스턴스 입니다.')

            # 보유 크레딧 확인
            member = reservation.member
            price = reservation.car.carprice
            min_price, mid_price, max_price = price.min_price_per_km, price.mid_price_per_km, price.max_price_per_km
            miles_credit = payment_price(attrs['distance'], min_price, mid_price, max_price)

            if member.profile.credit_point < miles_credit:
                raise serializers.ValidationError('보유 크레딧이 부족합니다.')
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException
        return attrs

    def create(self, validated_data):
        reservation = Reservation.objects.get(pk=validated_data['reservation_id'])
        payment = Payment.objects.create(distance=validated_data['distance'])
        reservation.payment = payment
        reservation.is_finished = True
        reservation.save()

        member = reservation.member
        member.profile.credit_point -= payment.miles_credit()
        member.profile.save()
        return payment

    def to_representation(self, instance):
        return PaymentSerializer(instance).data
