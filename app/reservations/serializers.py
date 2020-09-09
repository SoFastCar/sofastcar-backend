from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from cars.models import Car
from reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source='id')
    paid_credit = serializers.SerializerMethodField('get_paid_credit')

    class Meta:
        model = Reservation
        fields = (
            'reservation_id',
            'member',
            'car',
            'insurance',
            'from_when',
            'to_when',
            'rental_date',
            'is_finished',
            'paid_credit',
        )

    def get_paid_credit(self, obj):
        return obj.reservation_credit()


class ReservationCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    insurance = serializers.CharField()
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()

    def create(self, validated_data):
        try:
            car = Car.objects.get(pk=validated_data.get('car_id'))

            # 이용가능한 car 선택했다고 가정하고 생성 (exception 추가 예정)
            reservation = Reservation.objects.create(car=car, **validated_data)

            # 해당 사용자의 크레딧에서 요금 차감
            reservation.member.profile.credit_point -= reservation.reservation_credit()
            reservation.member.profile.save()
            return reservation
        except ObjectDoesNotExist:
            raise ValueError('해당하는 car 인스턴스가 존재하지 않습니다.')

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationInsuranceUpdateSerializer(serializers.Serializer):
    insurance = serializers.CharField()

    def update(self, instance, validated_data):
        paid_credit = instance.reservation_credit()
        instance.insurance = validated_data['insurance']
        instance.save()

        if instance.reservation_credit() > paid_credit:
            instance.member.profile.credit_point -= (instance.reservation_credit() - paid_credit)
        elif instance.reservation_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.reservation_credit())
        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationTimeUpdateSerializer(serializers.Serializer):
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()

    def update(self, instance, validated_data):
        paid_credit = instance.reservation_credit()
        reserved_times = instance.car.reservations.exclude(pk=instance.pk).filter(is_finished=False).values(
            'from_when', 'to_when'
        )

        if reserved_times:
            for time in reserved_times:
                if (
                        validated_data['from_when'] < time['to_when'] < validated_data['to_when']
                ) or (
                        validated_data['from_when'] < time['from_when'] < validated_data['to_when']
                ) or (
                        validated_data['from_when'] > time['from_when'] and validated_data['to_when'] < time['to_when']
                ):
                    raise ValueError('해당 이용시간대는 사용 불가능합니다.')

        instance.from_when = validated_data['from_when']
        instance.to_when = validated_data['to_when']
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.reservation_credit() > paid_credit:
            instance.member.profile.credit_point -= (instance.reservation_credit() - paid_credit)
        elif instance.reservation_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.reservation_credit())

        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class CarReservedTimesSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField(source='id')
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()
