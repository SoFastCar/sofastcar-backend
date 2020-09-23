from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
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
            'manufacturer',
            'fuel_type',
            'type_of_vehicle',
            'shift_type',
            'seater',
            'safety_option',
            'convenience_option',
        )

    def get_price(self, car):
        time_from = self.context.get('time_from')
        time_to = self.context.get('time_to')
        return car_rental_price(car.carprice.standard_price, time_from, time_to)


class CarzoneAvailableCarsSerializer(serializers.ModelSerializer):
    insurances = serializers.SerializerMethodField('get_insurances')
    cars = serializers.SerializerMethodField('get_cars')

    class Meta:
        model = CarZone
        fields = (
            'address',
            'type',
            'name',
            'insurances',
            'cars',
        )

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

        cars = list(chain(reservation_none_cars, available_time_cars))

        context = {
            'time_from': time_from,
            'time_to': time_to
        }

        serializer = CarsSerializer(instance=cars, many=True, context=context)
        return serializer.data


class AlarmCarSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField(source='id')
    seater = serializers.IntegerField(source='riding_capacity')
    standard_price = serializers.IntegerField(source='carprice.standard_price')
    miles_min_price = serializers.IntegerField(source='carprice.min_price_per_km')
    miles_max_price = serializers.IntegerField(source='carprice.max_price_per_km')

    class Meta:
        model = Car
        fields = (
            'car_id',
            'number',
            'name',
            'image',
            'manufacturer',
            'type_of_vehicle',
            'fuel_type',
            'shift_type',
            'seater',
            'safety_option',
            'convenience_option',
            'standard_price',
            'miles_min_price',
            'miles_max_price',
        )


class AddressSerializer(serializers.ModelSerializer):
    carzone_id = serializers.IntegerField(source='id')

    class Meta:
        model = CarZone
        fields = (
            'carzone_id',
            'address',
            'name',
            'sub_info',
            'detail_info',
            'type',
            'operating_time',
        )


# 대여 정보 확인
class ReservationSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source='id')
    rental_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    from_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    time = serializers.SerializerMethodField('get_time')  # format 수정 필요
    car = AlarmCarSerializer()
    carzone = AddressSerializer(source='car.zone')

    class Meta:
        model = Reservation
        fields = (
            'reservation_id',
            'rental_date',
            'insurance',
            'from_when',
            'to_when',
            'time',
            'rental_standard_credit',
            'rental_insurance_credit',
            'rental_credit',
            'car',
            'carzone',
        )

    def get_time(self, reservation):
        time = reservation.time()
        return f'{int(time)}분'


class ReservationCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    insurance = serializers.CharField(required=False)
    from_when = serializers.CharField()
    to_when = serializers.CharField()

    def validate(self, attrs):
        time_from = time_format(attrs['from_when'])
        time_to = time_format(attrs['to_when'])
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

        # 보유 크레딧 확인
        standard_credit = car_rental_price(car.carprice.standard_price, time_from, time_to)
        insurance_credit = insurance_price(attrs['insurance'], time_from, time_to)

        if member.profile.credit_point < standard_credit + insurance_credit:
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

            # 크레딧 차감
            reservation.member.profile.credit_point -= reservation.rental_credit()
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
        standard_credit = car_rental_price(reservation.car.carprice.standard_price, from_when, to_when)
        insurance_credit = insurance_price(insurance, from_when, to_when)
        rental_credit = insurance_credit + standard_credit

        if reservation.member.profile.credit_point < (rental_credit - reservation.rental_credit()):
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return insurance

    def update(self, instance, validated_data):
        paid_credit = instance.rental_credit()
        instance.insurance = validated_data['insurance']
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.rental_credit() > paid_credit:
            instance.member.profile.credit_point -= (instance.rental_credit() - paid_credit)
        elif instance.rental_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.rental_credit())
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

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= reservation.from_when:
            raise serializers.ValidationError('예약된 이용시간 이후에는 변경할 수 없습니다.')

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
        standard_credit = car_rental_price(car.carprice.standard_price, time_from, time_to)
        insurance_credit = insurance_price(reservation.insurance, time_from, time_to)
        rental_credit = insurance_credit + standard_credit

        if reservation.member.profile.credit_point < rental_credit:
            raise serializers.ValidationError('크레딧이 부족합니다.')
        return attrs

    def update(self, instance, validated_data):
        paid_credit = instance.rental_credit()
        instance.from_when = time_format(validated_data['from_when'])
        instance.to_when = time_format(validated_data['to_when'])
        instance.save()

        # 달라진 요금에 따라 해당 사용자의 크레딧 차감 혹은 적립
        if instance.rental_credit() > paid_credit:
            instance.member.profile.credit_point -= (instance.rental_credit() - paid_credit)
        elif instance.rental_credit() < paid_credit:
            instance.member.profile.credit_point += (paid_credit - instance.rental_credit())
        instance.member.profile.save()
        return instance

    def to_representation(self, instance):
        return ReservationSerializer(instance).data


class CarReservedTimesSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField(source='id')
    from_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)
    to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)


class ReservationExtensionSerializer(serializers.ModelSerializer):
    reservation_id = serializers.IntegerField(source='id')
    extended_to_when = serializers.DateTimeField(format='%Y-%m-%d %H:%M', default_timezone=KST)

    class Meta:
        model = Reservation
        fields = (
            'reservation_id',
            'extended_to_when',
            'extended_standard_credit',
            'extended_insurance_credit',
            'extended_credit',
        )


class ReservationTimeExtensionUpdateSerializer(serializers.Serializer):
    extended_to_when = serializers.CharField()

    def validate_extended_to_when(self, extended_to_when):
        reservation = self.context.get('reservation')
        from_when = reservation.from_when
        to_when = reservation.to_when
        extended_to = time_format(extended_to_when)

        if reservation.is_extended:
            reservation_to_when = reservation.extended_to_when
        elif not reservation.is_extended:
            reservation_to_when = to_when
        # else 구문 없으면 reservation_to_when을 밑에서 쓸 수 없음..
        else:
            raise serializers.ValidationError('해당 reservation의 반납 연장 여부를 알 수 없습니다. 서버 관리자에게 문의해 주세요.')

        # 예약 시작 < 현재 < 예약 반납 < 연장 반납 시간 확인
        if not (from_when < timezone.now() < reservation_to_when < extended_to):
            raise serializers.ValidationError('반납 연장은 예약된 이용시간 이후로 가능합니다.')

        # 반납된 예약이 아닌지 확인
        if reservation.is_finished:
            raise serializers.ValidationError('이미 반납된 reservation 인스턴스입니다.')
        return extended_to_when

    def update(self, instance, validated_data):
        reservation = self.context.get('reservation')
        reservation.is_extended = True
        reservation.extended_to_when = time_format(validated_data['extended_to_when'])
        reservation.save()
        return reservation

    def to_representation(self, instance):
        return ReservationExtensionSerializer(instance).data
