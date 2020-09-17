from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from payment.models import Payment
from reservations.exceptions import ReservationDoesNotExistException
from reservations.models import Reservation
from reservations.serializers import ReservationSerializer


class PaymentSerializer(serializers.ModelSerializer):
    payment_id = serializers.IntegerField(source='id')
    reservation = ReservationSerializer()

    class Meta:
        model = Payment
        fields = (
            'payment_id',
            'distance',
            'miles_credit',
            'extended_standard_credit',
            'extended_insurance_credit',
            'total_credit',
            'reservation',
        )


class PaymentCreateSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    distance = serializers.FloatField()

    def validate_reservation_id(self, reservation_id):
        try:
            reservation = Reservation.objects.get(pk=reservation_id)

            if reservation.payment:
                raise serializers.ValidationError('해당 reservation은 이미 결제되었습니다.')
            return reservation_id

        except ObjectDoesNotExist:
            raise ReservationDoesNotExistException

    def create(self, validated_data):
        reservation = Reservation.objects.get(pk=validated_data['reservation_id'])
        payment = Payment.objects.create(distance=validated_data['distance'])
        reservation.payment = payment
        reservation.is_finished = True
        reservation.save()
        return payment

    def to_representation(self, instance):
        return PaymentSerializer(instance).data
