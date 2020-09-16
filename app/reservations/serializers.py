import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from cars.models import Car
from reservations.exceptions import (
    NotAvailableCarException, ShortCreditException, TooLessOrTooMuchTimeException, AlreadyReservedTimeException,
    CarDoesNotExistException, BeforeTheCurrentTimeException
)
from reservations.models import Reservation
from reservations.utils import insurance_price, car_rental_price


class ReservationSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source='id')
    carzone = serializers.IntegerField(source='car.zone.id')
    rental_credit = serializers.SerializerMethodField('get_rental_credit')
    insurance_credit = serializers.SerializerMethodField('get_insurance_credit')
    total_credit = serializers.SerializerMethodField('get_total_credit')

    class Meta:
        model = Reservation
        fields = (
            'reservation_id',
            'member',
            'car',
            'carzone',
            'rental_credit',
            'insurance_credit',
            'total_credit',
            'from_when',
            'to_when',
            'rental_date',
            'is_finished',
        )

    def get_rental_credit(self, reservation):
        return reservation.rental_credit()

    def get_insurance_credit(self, reservation):
        return reservation.insurance_credit()

    def get_total_credit(self, reservation):
        return reservation.total_credit()


class ReservationCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    insurance = serializers.CharField(required=False)
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()

    def create(self, validated_data):
        try:
            car = Car.objects.get(pk=validated_data.get('car_id'))

            if not (30 * 60 <= (
                    validated_data['to_when'] - validated_data['from_when']).total_seconds() <= 30 * 60 * 24 * 60):
                raise TooLessOrTooMuchTimeException

            if validated_data['from_when'] <= timezone.now():
                raise BeforeTheCurrentTimeException

            reserved_times = car.reservations.filter(is_finished=False).values(
                'from_when', 'to_when'
            )
            if reserved_times:
                for time in reserved_times:
                    if (
                            validated_data['from_when'] <= time['to_when'] <= validated_data['to_when']
                    ) or (
                            validated_data['from_when'] <= time['from_when'] <= validated_data['to_when']
                    ) or (
                            validated_data['from_when'] >= time['from_when'] and validated_data['to_when'] <= time[
                        'to_when']
                    ):
                        raise AlreadyReservedTimeException

            reservation = Reservation.objects.create(car=car, **validated_data)

            if reservation.member.profile.credit_point < reservation.total_credit():
                reservation.delete()
                raise ShortCreditException
            else:
                # 해당 사용자의 크레딧에서 요금 차감
                reservation.member.profile.credit_point -= reservation.total_credit()
                reservation.member.profile.save()
                return reservation
        except ObjectDoesNotExist:
            raise CarDoesNotExistException

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationInsuranceUpdateSerializer(serializers.Serializer):
    insurance = serializers.CharField()

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        existing_insurance = instance.insurance
        instance.insurance = validated_data['insurance']
        instance.save()

        if instance.total_credit() > paid_credit:
            if instance.member.profile.credit_point < (instance.total_credit() - paid_credit):
                instance.insurance = existing_insurance
                instance.save()
                raise ShortCreditException
            else:
                instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)

        elif instance.total_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.total_credit())
        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationTimeUpdateSerializer(serializers.Serializer):
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        existing_from_when = instance.from_when
        existing_to_when = instance.to_when
        reserved_times = instance.car.reservations.exclude(pk=instance.pk).filter(is_finished=False).values(
            'from_when', 'to_when'
        )

        if not (30 * 60 <= (
                validated_data['to_when'] - validated_data['from_when']).total_seconds() <= 30 * 60 * 24 * 60):
            raise TooLessOrTooMuchTimeException

        if validated_data['from_when'] <= timezone.now():
            raise BeforeTheCurrentTimeException

        if reserved_times:
            for time in reserved_times:
                if (
                        validated_data['from_when'] <= time['to_when'] <= validated_data['to_when']
                ) or (
                        validated_data['from_when'] <= time['from_when'] <= validated_data['to_when']
                ) or (
                        validated_data['from_when'] >= time['from_when'] and validated_data['to_when'] <= time[
                    'to_when']
                ):
                    raise AlreadyReservedTimeException

        instance.from_when = validated_data['from_when']
        instance.to_when = validated_data['to_when']
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.total_credit() > paid_credit:
            if instance.member.profile.credit_point < (instance.total_credit() - paid_credit):
                instance.from_when = existing_from_when
                instance.to_when = existing_to_when
                instance.save()
                raise ShortCreditException
            else:
                instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)
        elif instance.total_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.total_credit())

        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationCarUpdateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        existing_car = instance.car

        car = Car.objects.get(pk=validated_data['car_id'])

        if car not in self.context.get('cars'):
            raise NotAvailableCarException

        instance.car = car
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.total_credit() > paid_credit:
            if instance.member.profile.credit_point < (instance.total_credit() - paid_credit):
                instance.car = existing_car
                instance.save()
                raise ShortCreditException
            else:
                instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)

        elif instance.total_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.total_credit())

        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class CarReservedTimesSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField(source='id')
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()


class CarsSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField(source='id')
    price = serializers.SerializerMethodField('get_price')
    seater = serializers.IntegerField(source='riding_capacity')

    class Meta:
        model = Car
        fields = (
            'car_id',
            'image',
            'name',
            'price',
            'seater',
        )

    def get_price(self, car):
        if type(self.context.get('to_when')) == str:
            to_when = datetime.datetime.strptime(self.context.get('to_when'), '%Y-%m-%dT%H:%M:%S.%f')
            from_when = datetime.datetime.strptime(self.context.get('from_when'), '%Y-%m-%dT%H:%M:%S.%f')
        else:
            to_when = self.context.get('to_when')
            from_when = self.context.get('from_when')
        return car_rental_price(car.carprice.standard_price, from_when, to_when)


class CarzoneAvailableCarsSerializer(serializers.Serializer):
    address = serializers.CharField()
    # image = serializers.ImageField()
    from_when = serializers.SerializerMethodField('get_from_when')
    to_when = serializers.SerializerMethodField('get_to_when')
    insurances = serializers.SerializerMethodField('get_insurances')
    cars = serializers.SerializerMethodField('get_cars')

    def get_from_when(self, carzone):
        return self.context.get('from_when')

    def get_to_when(self, carzone):
        return self.context.get('to_when')

    def get_insurances(self, carzone):
        to_when = datetime.datetime.strptime(self.context.get('to_when'), '%Y-%m-%dT%H:%M:%S.%f')
        from_when = datetime.datetime.strptime(self.context.get('from_when'), '%Y-%m-%dT%H:%M:%S.%f')

        return {
            'special': insurance_price('special', from_when, to_when),
            'standard': insurance_price('standard', from_when, to_when),
            'light': insurance_price('light', from_when, to_when),
        }

    def get_cars(self, carzone):
        cars = carzone.cars.exclude(reservations__is_finished=True).exclude(
            reservations__from_when__lte=self.context.get('to_when'),
            reservations__to_when__gte=self.context.get('to_when')
        ).exclude(
            reservations__from_when__lte=self.context.get('from_when'),
            reservations__to_when__gte=self.context.get('from_when')
        ).exclude(
            reservations__from_when__gte=self.context.get('from_when'),
            reservations__to_when__lte=self.context.get('to_when')
        )

        context = {
            'from_when': self.context.get('from_when'),
            'to_when': self.context.get('to_when')
        }

        serializer = CarsSerializer(instance=cars, many=True, context=context)
        return serializer.data
