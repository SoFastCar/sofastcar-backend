import datetime

import pytz
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cars.models import Car
from members.models import Member
from reservations.models import Reservation


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

        # 차량 존재, 이용시간대 중복 체크
        if Car.objects.filter(id=self.context['view'].kwargs.get('car_pk')).exists():
            car = Car.objects.get(id=self.context['view'].kwargs.get('car_pk'))
            if car.time_tables.filter(Q(date_time_start__lte=date_time_start, date_time_end__gte=date_time_end) |
                                      Q(date_time_start__gte=date_time_end, date_time_end__lte=date_time_end) |
                                      Q(date_time_start__gte=date_time_start, date_time_end__gte=date_time_start)):
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
        total_rental_price = car_rental_price + insurance_price

        # 크레딧 잔고 체크
        member = Member.objects.get(email=self.context['view'].request.user)
        if member.profile.credit_point < total_rental_price:
            raise serializers.ValidationError('크레딧 잔액이 부족합니다.')
        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
