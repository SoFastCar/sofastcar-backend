from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from cars.models import Car
from core.exceptions import ReservationDoesNotExistException
from core.utils import payment_price, KST
from payment.models import Payment
from reservations.models import Reservation


class PricesSerializer(serializers.ModelSerializer):
    total_credit = serializers.SerializerMethodField('get_total_credit')
    before_run_credit = serializers.IntegerField(source='rental_credit')
    after_run_credit = serializers.SerializerMethodField('get_after_run_credit')
    miles_credit = serializers.IntegerField(source='payment.miles_credit')
    miles_min_price = serializers.IntegerField(source='car.carprice.min_price_per_km')
    miles_max_price = serializers.IntegerField(source='car.carprice.max_price_per_km')

    class Meta:
        model = Reservation
        fields = (
            'total_credit',
            'before_run_credit',
            'rental_standard_credit',
            'rental_insurance_credit',
            # 'coupon',
            'after_run_credit',
            'miles_credit',
            # 'hipass',
            'extended_standard_credit',
            'extended_insurance_credit',
            'miles_min_price',
            'miles_max_price',
        )

    def get_total_credit(self, reservation):
        total_credit = reservation.rental_credit() + reservation.extended_credit() + reservation.payment.miles_credit()
        return total_credit

    def get_after_run_credit(self, reservation):
        after_run_credit = reservation.payment.miles_credit() + reservation.extended_credit()
        return after_run_credit


class PaymentSerializer(serializers.ModelSerializer):
    payment_id = serializers.IntegerField(source='id')
    distance_credit = serializers.IntegerField(source='miles_credit')
    payment_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    car = serializers.CharField(source='reservation.car.number')
    # level = serializers.IntegerField(source='reservation.member.profile.level')  # level 필요할 듯..
    prices = serializers.SerializerMethodField('get_prices')

    class Meta:
        model = Payment
        fields = (
            'payment_id',
            'distance',
            'distance_credit',
            'payment_date',
            'car',
            # 'level',
            'prices',
        )

    def get_prices(self, payment):
        serializer = PricesSerializer(instance=payment.reservation)
        return serializer.data


class PaymentCreateSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    distance = serializers.FloatField()
    good = serializers.BooleanField(required=False)

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

            if member.profile.credit_point < miles_credit + reservation.extended_credit():
                raise serializers.ValidationError('보유 크레딧이 부족합니다.')
        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException
        return attrs

    def create(self, validated_data):
        reservation = Reservation.objects.get(pk=validated_data['reservation_id'])
        payment = Payment.objects.create(distance=validated_data['distance'], good=validated_data['good'])
        reservation.payment = payment
        reservation.is_finished = True
        reservation.save()

        # (주행료 + 반납연장 추가요금) 차감
        member = reservation.member
        member.profile.credit_point -= (payment.miles_credit() + reservation.extended_credit())
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


class PaymentRentalHistorySerializer(serializers.Serializer):
    payment_id = serializers.IntegerField(source='id')
    reservation = ReservationHistorySerializer()
    payment = serializers.SerializerMethodField('get_payment')

    def get_payment(self, payment):
        serializer = PaymentSerializer(instance=payment)
        return serializer.data
