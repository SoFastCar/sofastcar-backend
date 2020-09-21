from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from cars.models import Car
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


class ReservationHistoryCarSerializer(serializers.ModelSerializer):
    min_price = serializers.IntegerField(source='carprice.min_price_per_km')
    max_price = serializers.IntegerField(source='carprice.max_price_per_km')

    class Meta:
        model = Car
        fields = (
            'number',
            'manufacturer',
            'min_price',
            'max_price',
        )


class ReservationHistorySerializer(serializers.ModelSerializer):
    from_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    time = serializers.SerializerMethodField('get_time')
    car = ReservationHistoryCarSerializer()
    address = serializers.CharField(source='car.zone.address')

    class Meta:
        model = Reservation
        fields = (
            'from_when',
            'to_when',
            'time',
            'car',
            'address',
        )

    def get_time(self, reservation):
        time = int(reservation.time())
        return f'{time}분'


class PaymentHistorySerializer(serializers.ModelSerializer):
    rental_credit = serializers.IntegerField(source='reservation.rental_credit')
    insurance_credit = serializers.IntegerField(source='reservation.insurance_credit')
    extended_rental_credit = serializers.IntegerField(source='reservation.extended_rental_credit')
    extended_insurance_credit = serializers.IntegerField(source='reservation.extended_insurance_credit')
    reservation_total_credit = serializers.IntegerField(source='reservation.total_credit')

    class Meta:
        model = Payment
        fields = (
            'rental_credit',
            'insurance_credit',
            'extended_rental_credit',
            'extended_insurance_credit',
            'reservation_total_credit',
            'miles_credit',
        )


class PaymentRentalHistorySerializer(serializers.Serializer):
    payment_id = serializers.IntegerField(source='id')
    reservation = ReservationHistorySerializer()
    payment = serializers.SerializerMethodField('get_payment')

    def get_payment(self, payment):
        serializer = PaymentHistorySerializer(instance=payment)
        return serializer.data
