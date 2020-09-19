import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from cars.models import Car
from carzones.models import CarZone
from core.utils import insurance_price, car_rental_price
from core.exceptions import CarDoesNotExistException
from reservations.models import Reservation


class CarZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarZone
        fields = (
            'id',
            'address',
            'name',
            'region',
            'sub_info',
            'detail_info',
            'type',
            'operating_time',
        )


class ReservationSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source='id')
    carzone = CarZoneSerializer(source='car.zone')

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


class ReservationCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    insurance = serializers.CharField(required=False)
    from_when = serializers.DateTimeField()
    to_when = serializers.DateTimeField()

    # 현재 예약 시작시간 이전인지 확인
    def validate_from_when(self, from_when):
        if timezone.now() >= from_when:
            raise serializers.ValidationError('현재 시간 이후부터 예약 가능합니다.')
        return from_when

    def validate(self, attrs):
        from_when = attrs['from_when']
        to_when = attrs['to_when']
        insurance = attrs['insurance']
        car = Car.objects.get(pk=attrs['car_id'])
        member = self.context.get('member')

        # 이용시간대 30분 이상 30일 이하 확인
        MIN_DURATION = 30 * 60
        MAX_DURATION = 30 * 60 * 24 * 60

        if not MIN_DURATION <= (to_when - from_when).total_seconds() <= MAX_DURATION:
            raise serializers.ValidationError('최소 30분부터 최대 30일까지 설정 가능합니다.')

        # 해당 car_id의 예약가능한 시간대 확인
        reservations = car.reservations.filter(is_finished=False)

        if (
                reservations.filter(from_when__lte=to_when, to_when__gte=to_when)
        ) or (
                reservations.filter(from_when__lte=from_when, to_when__gte=from_when)
        ) or (
                reservations.filter(from_when__gte=from_when, to_when__lte=to_when)
        ):
            raise serializers.ValidationError('해당 이용시간대는 사용 불가능합니다.')

        # 해당 member의 크레딧 확인
        insurance_credit = insurance_price(insurance, from_when, to_when)
        rental_credit = car_rental_price(car.carprice.standard_price, from_when, to_when)
        total_credit = insurance_credit + rental_credit

        if member.profile.credit_point < total_credit:
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return attrs

    def create(self, validated_data):
        try:
            car = Car.objects.get(pk=validated_data.get('car_id'))
            reservation = Reservation.objects.create(car=car, **validated_data)

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

    # 해당 member의 크레딧 확인
    def validate_insurance(self, insurance):
        reservation = self.context.get('reservation')

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= reservation.from_when:
            raise serializers.ValidationError('예약된 이용시간 이후에는 변경할 수 없습니다.')

        # 보유 크레딧 확인
        insurance_credit = insurance_price(insurance, reservation.from_when, reservation.to_when)
        rental_credit = car_rental_price(reservation.car.carprice.standard_price, reservation.from_when,
                                         reservation.to_when)
        total_credit = insurance_credit + rental_credit

        if reservation.member.profile.credit_point < (total_credit - reservation.total_credit()):
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return insurance

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        instance.insurance = validated_data['insurance']
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.total_credit() > paid_credit:
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

    # 예약시간대 현재 시간 이후인지 확인
    def validate_from_when(self, from_when):
        if timezone.now() >= from_when:
            raise serializers.ValidationError('변경할 이용시작시간은 현재 이후여야 합니다.')
        return from_when

    def validate(self, attrs):
        from_when = attrs['from_when']
        to_when = attrs['to_when']
        reservation = self.context.get('reservation')
        car = reservation.car

        # 이용시간대 30분 이상 30일 이하 확인
        MIN_DURATION = 30 * 60
        MAX_DURATION = 30 * 60 * 24 * 60

        if not MIN_DURATION <= (to_when - from_when).total_seconds() <= MAX_DURATION:
            raise serializers.ValidationError('최소 30분부터 최대 30일까지 설정 가능합니다.')

        # 해당 car_id의 예약가능한 시간대 확인
        reservations = car.reservations.exclude(pk=reservation.id).filter(is_finished=False)

        if (
                reservations.filter(from_when__lte=to_when, to_when__gte=to_when)
        ) or (
                reservations.filter(from_when__lte=from_when, to_when__gte=from_when)
        ) or (
                reservations.filter(from_when__gte=from_when, to_when__lte=to_when)
        ):
            raise serializers.ValidationError('해당 이용시간대는 사용 불가능합니다.')

        # 해당 member의 크레딧 확인
        insurance_credit = insurance_price(reservation.insurance, from_when, to_when)
        rental_credit = car_rental_price(car.carprice.standard_price, from_when, to_when)
        total_credit = insurance_credit + rental_credit

        if reservation.member.profile.credit_point < total_credit:
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return attrs

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        instance.from_when = validated_data['from_when']
        instance.to_when = validated_data['to_when']
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.total_credit() > paid_credit:
            instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)
        elif instance.total_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.total_credit())
        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationCarUpdateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()

    def validate_car_id(self, car_id):
        reservation = self.context.get('reservation')

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= reservation.from_when:
            raise serializers.ValidationError('현재 시간 이후부터 변경 가능합니다.')

        try:
            car = Car.objects.get(pk=car_id)

            # 해당 carzone에 속하는 car인지 확인
            if car not in self.context.get('cars'):
                raise serializers.ValidationError('해당 carzone에서 이용가능한 car id가 아닙니다.')

            # 해당 member의 크레딧 확인
            insurance_credit = insurance_price(reservation.insurance, reservation.from_when, reservation.to_when)
            rental_credit = car_rental_price(car.carprice.standard_price, reservation.from_when, reservation.to_when)
            total_credit = insurance_credit + rental_credit

            if reservation.member.profile.credit_point < (total_credit - reservation.total_credit()):
                raise serializers.ValidationError('크레딧이 부족합니다.')
            return car_id

        except ObjectDoesNotExist:
            raise CarDoesNotExistException

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        car = Car.objects.get(pk=validated_data['car_id'])
        instance.car = car
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.total_credit() > paid_credit:
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


class ReservationTimeExtensionUpdateSerializer(serializers.Serializer):
    extended_to_when = serializers.DateTimeField()

    def validate_extended_to_when(self, extended_to_when):
        reservation = self.context.get('reservation')
        member = reservation.member

        if reservation.is_extended:
            reservation_to_when = reservation.extended_to_when
        elif not reservation.is_extended:
            reservation_to_when = reservation.to_when
        else:
            raise serializers.ValidationError('해당 reservation의 반납 연장 여부를 알 수 없습니다. 서버 관리자에게 문의해 주세요.')

        # 예약 시작 < 현재 < 예약 반납 < 연장 반납 시간 확인
        if not (reservation.from_when < timezone.now() < reservation_to_when < extended_to_when):
            raise serializers.ValidationError('예약된 이용시간 이전에는 반납 연장할 수 없습니다.')

        # 반납된 예약이 아닌지 확인
        if reservation.is_finished:
            raise serializers.ValidationError('이미 반납된 reservation 인스턴스입니다.')

        # 보유 크레딧 확인
        extended_rental_credit = car_rental_price(reservation.car.carprice.standard_price, reservation.to_when,
                                                  extended_to_when)
        extended_insurance_credit = insurance_price(reservation.insurance, reservation.to_when, extended_to_when)
        total_credit = reservation.rental_credit() + reservation.insurance_credit() + extended_rental_credit + extended_insurance_credit

        if member.profile.credit_point < total_credit - reservation.total_credit():
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return extended_to_when

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        reservation = self.context.get('reservation')
        reservation.is_extended = True
        reservation.extended_to_when = validated_data['extended_to_when']
        reservation.save()

        # 연장된 요금에 따라 해당 사용자의 크레딧 차감
        instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)
        instance.member.profile.save()
        return reservation
