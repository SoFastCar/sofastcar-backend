from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone
from rest_framework import serializers

from cars.models import Car
from carzones.models import CarZone
from core.utils import insurance_price, car_rental_price, time_format, KST
from core.exceptions import CarDoesNotExistException
from reservations.models import Reservation


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
        time_from = self.context.get('time_from')
        time_to = self.context.get('time_to')
        return car_rental_price(car.carprice.standard_price, time_from, time_to)


class CarzoneAvailableCarsSerializer(serializers.ModelSerializer):
    from_when = serializers.SerializerMethodField('get_from_when')
    to_when = serializers.SerializerMethodField('get_to_when')
    insurances = serializers.SerializerMethodField('get_insurances')
    cars = serializers.SerializerMethodField('get_cars')

    class Meta:
        model = CarZone
        fields = (
            'address',
            'from_when',
            'to_when',
            'insurances',
            'cars',
        )

    # 원하는 datetime 포맷으로 안나옴 (수정 필요)
    def get_from_when(self, carzone):
        time_from = self.context.get('time_from')
        return time_from.astimezone(KST)

    def get_to_when(self, carzone):
        time_to = self.context.get('time_to')
        return time_to.astimezone(KST)

    def get_insurances(self, carzone):
        time_from = self.context.get('time_from')
        time_to = self.context.get('time_to')

        return {
            'special': insurance_price('special', time_from, time_to),
            'standard': insurance_price('standard', time_from, time_to),
            'light': insurance_price('light', time_from, time_to),
        }

    def get_cars(self, carzone):
        time_from = self.context.get('time_from')
        time_to = self.context.get('time_to')

        # reservation 인스턴스가 아예 없는 cars
        reservation_none_cars = carzone.cars.annotate(cnt=Count('reservations')).filter(cnt=0)
        # 해당 이용시간대와 겹치는 reservation 인스턴스가 없는 cars
        available_time_cars = carzone.cars.filter(
            reservations__is_finished=False
        ).exclude(
            reservations__from_when__lte=time_to, reservations__to_when__gte=time_to
        ).exclude(
            reservations__from_when__lte=time_from, reservations__to_when__gte=time_from
        ).exclude(
            reservations__from_when__gte=time_from, reservations__to_when__lte=time_to
        )
        cars = available_time_cars or reservation_none_cars

        context = {
            'time_from': time_from,
            'time_to': time_to
        }

        serializer = CarsSerializer(instance=cars, many=True, context=context)
        return serializer.data


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
    from_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    extended_to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    rental_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)

    class Meta:
        model = Reservation
        fields = (
            'reservation_id',
            'member',
            'car',
            'carzone',
            'is_extended',
            'rental_credit',
            'insurance_credit',
            'extended_rental_credit',
            'extended_insurance_credit',
            'total_credit',
            'from_when',
            'to_when',
            'extended_to_when',
            'rental_date',
            'is_finished',
        )


class ReservationCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    insurance = serializers.CharField(required=False)
    from_when = serializers.CharField()
    to_when = serializers.CharField()

    def validate(self, attrs):
        time_from = time_format(attrs['from_when'])
        time_to = time_format(attrs['to_when'])
        insurance = attrs['insurance']
        car = Car.objects.get(pk=attrs['car_id'])
        member = self.context.get('member')

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= time_from:
            raise serializers.ValidationError('현재 시간 이후부터 예약 가능합니다.')

        # 이용시간대 30분 이상 30일 이하 확인
        MIN_DURATION = 30 * 60
        MAX_DURATION = 30 * 60 * 24 * 60

        if not MIN_DURATION <= (time_to - time_from).total_seconds() <= MAX_DURATION:
            raise serializers.ValidationError('최소 30분부터 최대 30일까지 설정 가능합니다.')

        # 해당 car_id의 예약가능한 시간대 확인
        reservations = car.reservations.filter(is_finished=False)

        if (
                reservations.filter(from_when__lte=time_to, to_when__gte=time_to)
        ) or (
                reservations.filter(from_when__lte=time_from, to_when__gte=time_from)
        ) or (
                reservations.filter(from_when__gte=time_from, to_when__lte=time_to)
        ):
            raise serializers.ValidationError('해당 이용시간대는 사용 불가능합니다.')

        # 해당 member의 크레딧 확인
        insurance_credit = insurance_price(insurance, time_from, time_to)
        rental_credit = car_rental_price(car.carprice.standard_price, time_from, time_to)
        total_credit = insurance_credit + rental_credit

        if member.profile.credit_point < total_credit:
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return attrs

    def create(self, validated_data):
        try:
            time_from = time_format(validated_data['from_when'])
            time_to = time_format(validated_data['to_when'])
            insurance = validated_data['insurance']
            member = self.context.get('member')
            car = Car.objects.get(pk=validated_data.get('car_id'))

            reservation = Reservation.objects.create(car=car, member=member, from_when=time_from, to_when=time_to,
                                                     insurance=insurance)

            # 해당 사용자의 크레딧에서 요금 차감
            reservation.member.profile.credit_point -= reservation.total_credit()
            reservation.member.profile.save()
            return reservation

        except ObjectDoesNotExist:
            raise CarDoesNotExistException

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class ReservationInsuranceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            'insurance',
        )

    # 해당 member의 크레딧 확인
    def validate_insurance(self, insurance):
        reservation = self.context.get('reservation')
        from_when = reservation.from_when
        to_when = reservation.to_when

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= from_when:
            raise serializers.ValidationError('예약된 이용시간 이후에는 변경할 수 없습니다.')

        # 보유 크레딧 확인
        insurance_credit = insurance_price(insurance, from_when, to_when)
        rental_credit = car_rental_price(reservation.car.carprice.standard_price, from_when, to_when)
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
    from_when = serializers.CharField()
    to_when = serializers.CharField()

    def validate(self, attrs):
        time_from = time_format(attrs['from_when'])
        time_to = time_format(attrs['to_when'])
        reservation = self.context.get('reservation')
        car = reservation.car

        # 예약시간대 현재 시간 이후인지 확인
        if timezone.now() >= time_from:
            raise serializers.ValidationError('변경할 이용시작시간은 현재 이후여야 합니다.')

        # 이용시간대 30분 이상 30일 이하 확인
        MIN_DURATION = 30 * 60
        MAX_DURATION = 30 * 60 * 24 * 60

        if not MIN_DURATION <= (time_to - time_from).total_seconds() <= MAX_DURATION:
            raise serializers.ValidationError('최소 30분부터 최대 30일까지 설정 가능합니다.')

        # 해당 car_id의 예약가능한 시간대 확인
        reservations = car.reservations.exclude(pk=reservation.id).filter(is_finished=False)

        if (
                reservations.filter(from_when__lte=time_to, to_when__gte=time_to)
        ) or (
                reservations.filter(from_when__lte=time_from, to_when__gte=time_from)
        ) or (
                reservations.filter(from_when__gte=time_from, to_when__lte=time_to)
        ):
            raise serializers.ValidationError('해당 이용시간대는 사용 불가능합니다.')

        # 해당 member의 크레딧 확인
        insurance_credit = insurance_price(reservation.insurance, time_from, time_to)
        rental_credit = car_rental_price(car.carprice.standard_price, time_from, time_to)
        total_credit = insurance_credit + rental_credit

        if reservation.member.profile.credit_point < total_credit:
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return attrs

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        instance.from_when = time_format(validated_data['from_when'])
        instance.to_when = time_format(validated_data['to_when'])
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
        from_when = reservation.from_when
        to_when = reservation.to_when

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= from_when:
            raise serializers.ValidationError('이미 예약시간이 지나 수정할 수 없습니다.')

        try:
            car = Car.objects.get(pk=car_id)

            if car == reservation.car:
                raise serializers.ValidationError('기존 예약된 car id와 같습니다.')

            # 해당 carzone에 속하는 car인지 확인
            if car not in self.context.get('cars'):
                raise serializers.ValidationError('해당 carzone에서 이용가능한 car id가 아닙니다.')

            # 해당 member의 크레딧 확인
            insurance_credit = insurance_price(reservation.insurance, from_when, to_when)
            rental_credit = car_rental_price(car.carprice.standard_price, from_when, to_when)
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
    from_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)


class ReservationTimeExtensionUpdateSerializer(serializers.Serializer):
    extended_to_when = serializers.CharField()

    def validate_extended_to_when(self, extended_to_when):
        reservation = self.context.get('reservation')
        from_when = reservation.from_when
        to_when = reservation.to_when
        member = reservation.member

        if reservation.is_extended:
            reservation_to_when = reservation.extended_to_when
            extended_to = time_format(extended_to_when)
        elif not reservation.is_extended:
            reservation_to_when = to_when
            extended_to = extended_to_when
        else:
            raise serializers.ValidationError('해당 reservation의 반납 연장 여부를 알 수 없습니다. 서버 관리자에게 문의해 주세요.')

        # 예약 시작 < 현재 < 예약 반납 < 연장 반납 시간 확인
        if not (from_when < timezone.now() < reservation_to_when < extended_to):
            raise serializers.ValidationError('반납 연장은 예약된 이용시간 이후로 가능합니다.')

        # 반납된 예약이 아닌지 확인
        if reservation.is_finished:
            raise serializers.ValidationError('이미 반납된 reservation 인스턴스입니다.')

        # 보유 크레딧 확인
        extended_rental_credit = car_rental_price(reservation.car.carprice.standard_price, to_when, extended_to)
        extended_insurance_credit = insurance_price(reservation.insurance, to_when, extended_to)
        total_credit = reservation.rental_credit() + reservation.insurance_credit() + extended_rental_credit + extended_insurance_credit

        if member.profile.credit_point < total_credit - reservation.total_credit():
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return extended_to_when

    def update(self, instance, validated_data):
        paid_credit = instance.total_credit()
        reservation = self.context.get('reservation')
        reservation.is_extended = True
        reservation.extended_to_when = time_format(validated_data['extended_to_when'])
        reservation.save()

        # 연장된 요금에 따라 해당 사용자의 크레딧 차감
        instance.member.profile.credit_point -= (instance.total_credit() - paid_credit)
        instance.member.profile.save()
        return reservation

    def to_representation(self, instance):
        return ReservationSerializer(instance).data
