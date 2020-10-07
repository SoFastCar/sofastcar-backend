import datetime

import pytz
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car
from core.utils import KST
from members.models import Member, Profile
from payments.models import PaymentAfterUse
from prices.models import Coupon
from reservations.models import Reservation, PhotoBeforeUse


class ReservationSerializer(ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id',
                  'member',
                  'car',
                  'zone',
                  'insurance',
                  'date_time_start',
                  'date_time_end',
                  'created_at',
                  'updated_at']
        read_only_fields = ['id',
                            'member',
                            'car',
                            'zone',
                            'created_at',
                            'updated_at']

    def validate_insurance(self, value):
        if value not in ('light', 'standard', 'special'):
            raise serializers.ValidationError('Wrong format, need this form like - ex) light, standard, special')
        return value

    def validate(self, attrs):
        date_time_start = attrs.get('date_time_start')
        date_time_end = attrs.get('date_time_end')
        insurance_type = attrs.get('insurance')

        # UTC 체크
        if date_time_start.tzinfo != pytz.utc or date_time_end.tzinfo != pytz.utc:
            raise serializers.ValidationError('UTC 시간대로 입력해야 합니다.')

        # 현재 예약 시작시간 이전인지 확인
        if timezone.now() >= date_time_start:
            raise serializers.ValidationError('현재 시간 이후부터 예약 가능합니다.')

        # 이용시간대 30분 이상 30일 이하 확인
        MIN_DURATION = 30 * 60
        MAX_DURATION = 30 * 60 * 24 * 60

        if not MIN_DURATION <= (date_time_end - date_time_start).total_seconds() <= MAX_DURATION:
            raise serializers.ValidationError('최소 30분부터 최대 30일까지 설정 가능합니다.')

        # 쿠폰 체크
        coupon_discount = 0
        member = Member.objects.get(email=self.context['view'].request.user)
        if Coupon.objects.filter(member_id=member.id, will_use_check=True, is_enabled=True).exists():
            if 2 < Coupon.objects.filter(member_id=member.id, will_use_check=True, is_enabled=True).count():
                raise serializers.ValidationError('쿠폰은 하나의 예약에 한개만 사용 가능합니다')
            coupon = Coupon.objects.get(member_id=member.id, will_use_check=True, is_enabled=True)
            coupon_discount = coupon.discount_fee

        # 차량 존재, 이용시간대 중복 체크
        if Car.objects.filter(id=self.context['view'].kwargs.get('car_pk')).exists():
            car = Car.objects.get(id=self.context['view'].kwargs.get('car_pk'))
            if car.time_tables.filter(Q(date_time_start__lte=date_time_start) & Q(date_time_end__gte=date_time_end) |
                                      Q(date_time_end__range=(date_time_start, date_time_end)) |
                                      Q(date_time_start__range=(date_time_start, date_time_end))).exists():
                raise serializers.ValidationError('해당 이용시간대는 사용 불가능합니다.')
        else:
            raise serializers.ValidationError('해당 차량이 존재하지 않습니다.')

        # 대여 가격
        car_rental_price = car.carprice.get_price_from_iso_format(date_time_start, date_time_end)
        if insurance_type == 'light':
            insurance_price = car.insurances.get_light_price_from_iso_format(date_time_start, date_time_end)
        elif insurance_type == 'standard':
            insurance_price = car.insurances.get_standard_price_from_iso_format(date_time_start, date_time_end)
        elif insurance_type == 'special':
            insurance_price = car.insurances.get_special_price_from_iso_format(date_time_start, date_time_end)
        total_rental_price = car_rental_price + insurance_price - coupon_discount

        # 크레딧 잔고 체크
        if Profile.objects.get(member_id=member.id).credit_point < total_rental_price:
            raise serializers.ValidationError('크레딧 잔액이 부족합니다.')
        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ReservationHistorySerializer(ModelSerializer):
    date_time_start = serializers.DateTimeField(read_only=True, default_timezone=KST)
    date_time_end = serializers.DateTimeField(read_only=True, default_timezone=KST)

    class Meta:
        model = Reservation
        fields = ['id',
                  'member',
                  'car',
                  'zone',
                  'insurance',
                  'date_time_start',
                  'date_time_end',
                  'created_at',
                  'updated_at']
        read_only_fields = ['id',
                            'member',
                            'car',
                            'zone',
                            'insurance',
                            'date_time_start',
                            'date_time_end',
                            'created_at',
                            'updated_at']


class UseHistoryListSerializer(ModelSerializer):
    reservation_status = serializers.SerializerMethodField()
    zone_name = serializers.CharField(read_only=True, source='zone.name')
    return_zone = serializers.CharField(read_only=True, source='zone.name')
    date_time_start = serializers.DateTimeField(read_only=True, default_timezone=KST)
    date_time_end = serializers.DateTimeField(read_only=True, default_timezone=KST)
    date_time_extension = serializers.DateTimeField(read_only=True, default_timezone=KST)
    car_name = serializers.CharField(read_only=True, source='car.name')
    car_number = serializers.CharField(read_only=True, source='car.number')
    car_image = serializers.ImageField(read_only=True, allow_null=True, source='car.image')
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id',
                  'reservation_status',
                  'member',
                  'zone',
                  'zone_name',
                  'return_zone',
                  'car',
                  'car_name',
                  'car_number',
                  'car_image',
                  'distance',
                  'date_time_start',
                  'date_time_end',
                  'date_time_extension',
                  ]
        read_only_fields = ['id',
                            'reservation_status',
                            'member',
                            'zone',
                            'zone_name',
                            'return_zone',
                            'car',
                            'car_name',
                            'car_number',
                            'car_image',
                            'distance',
                            'date_time_start',
                            'date_time_end',
                            'date_time_extension',
                            ]

    def get_reservation_status(self, obj):
        if obj.status.status == obj.status.ChoiceStatus.PAID_2:
            obj.status.status = obj.status.ChoiceStatus.FINISHED
            obj.status.save()
            return '반납완료'
        elif obj.status.status == obj.status.ChoiceStatus.PAID_1:
            if obj.date_time_start <= timezone.now() < obj.date_time_end:
                return '사용중'
            elif timezone.now() < obj.date_time_start:
                return '운행전결제완료'
            else:
                return '2차결제미납'
        elif obj.status.status == obj.status.ChoiceStatus.FINISHED:
            return '반납완료'
        elif obj.status.status == obj.status.ChoiceStatus.NOTPAID:
            return '운행전결제미납'
        elif obj.status.status == obj.status.ChoiceStatus.EXTENDED:
            if obj.date_time_start <= timezone.now() < obj.date_time_end:
                return '사용중'
            elif obj.date_time_end <= timezone.now() < obj.date_time_extension:
                return '연장중'
            elif obj.date_time_extension <= timezone.now():
                return '2차결제미납'

    def get_distance(self, obj):

        if PaymentAfterUse.objects.filter(reservation_id=obj.id).exists():
            return obj.payment_after.driving_distance
        else:
            return 0


class PhotoBeforeUseSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = PhotoBeforeUse
        fields = ['id', 'member', 'reservation', 'image', 'photos']
        read_only_fields = ['id', 'member', 'reservation', 'image']

    def validate(self, attrs):
        # 예약 존재 여부 확인
        if not Reservation.objects.filter(id=self.context['view'].kwargs['reservation_pk']).exists():
            raise serializers.ValidationError('Reservation does not exists')
        return attrs

    def create(self, validated_data):
        images_data = self.context['request'].FILES
        photo_bulk_list = []

        for image in images_data.getlist('photos'):
            photo = PhotoBeforeUse(
                reservation=validated_data.get('reservation'),
                image=image,
                member=self.context['request'].user)
            photo_bulk_list.append(photo)
        instance = PhotoBeforeUse.objects.bulk_create(photo_bulk_list)

        return instance
