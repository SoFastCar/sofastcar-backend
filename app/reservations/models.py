from django.db import models, transaction
from django.utils.translation import gettext as _


# Create your models here.
from payments.models import PaymentBeforeUse


class Reservation(models.Model):
    class ChoiceInsuranceType(models.TextChoices):
        SPECIAL = 'special', _('스페셜')
        STANDARD = 'standard', _('스탠다드')
        LIGHT = 'light', _('라이트')

    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='reservation_members')
    zone = models.ForeignKey('carzones.CarZone', on_delete=models.CASCADE, related_name='reservation_zones')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='reservation_cars')
    insurance = models.CharField(choices=ChoiceInsuranceType.choices, default=ChoiceInsuranceType.LIGHT,
                                 help_text='차량손해면책상품', max_length=30)
    date_time_start = models.DateTimeField(help_text='예약시작날짜시간')
    date_time_end = models.DateTimeField(help_text='예약종료날짜시간')
    date_time_extension = models.DateTimeField(null=True, help_text='연장종료날짜시간')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_extension = False
        # 대여 가격
        if self.id is None:
            car_rental_price = self.car.carprice.get_price_from_iso_format(self.date_time_start, self.date_time_end)
            if self.insurance == 'light':
                insurance_price = self.car.insurances.get_light_price_from_iso_format(self.date_time_start,
                                                                                      self.date_time_end)
            elif self.insurance == 'standard':
                insurance_price = self.car.insurances.get_standard_price_from_iso_format(self.date_time_start,
                                                                                         self.date_time_end)
            elif self.insurance == 'special':
                insurance_price = self.car.insurances.get_special_price_from_iso_format(self.date_time_start,
                                                                                        self.date_time_end)
        elif self.date_time_extension is not None:
            is_extension = True
            # 연장요금 계산
            extra_car_rental_price = self.car.carprice.get_price_from_iso_format(self.date_time_end,
                                                                                 self.date_time_extension)
            if self.insurance == 'light':
                extra_insurance_price = self.car.insurances.get_light_price_from_iso_format(self.date_time_end,
                                                                                            self.date_time_extension)
            elif self.insurance == 'standard':
                extra_insurance_price = self.car.insurances.get_standard_price_from_iso_format(self.date_time_end,
                                                                                               self.date_time_extension)
            elif self.insurance == 'special':
                extra_insurance_price = self.car.insurances.get_special_price_from_iso_format(self.date_time_end,
                                                                                              self.date_time_extension)
        if is_extension:
            # 연장 요금
            total_fee = extra_car_rental_price + extra_insurance_price
        else:
            # 기본 대여 요금
            total_fee = car_rental_price + insurance_price

        with transaction.atomic():
            # blance
            self.member.profile.credit_point -= total_fee
            self.member.profile.save()

            # Reservation save()
            super().save(force_insert, force_update, using, update_fields)
            if is_extension:
                # Extension Status save
                extension_status = ReservationStatus.objects.get(reservation_id=self.id)
                extension_status.status = ReservationStatus.ChoiceStatus.EXTENDED
                extension_status.save()

                # 기존 결제 정보에 연장료 추가 저장
                pay = PaymentBeforeUse.objects.get(reservation_id=self.id)
                pay.extension_fee = total_fee
                pay.total_fee = total_fee + pay.extension_fee
                pay.save()
            else:
                # paid_1 Status save
                ReservationStatus.objects.create(reservation_id=self.id,
                                                 status=ReservationStatus.ChoiceStatus.PAID_1)
                PaymentBeforeUse.objects.create(reservation_id=self.id,
                                                rental_fee=car_rental_price,
                                                insurance_fee=insurance_price,
                                                total_fee=total_fee)


class ReservationStatus(models.Model):
    class ChoiceStatus(models.TextChoices):
        NOTPAID = 'not_paid', _('결제전')
        PAID_1 = 'paid_1', _('운행전결제완료')
        PAID_2 = 'paid_2', _('운행후결제완료')
        USING = 'using', _('사용중')
        EXTENDED = 'extended', _('사용중추가연장')
        FINISHED = 'finished', _('반납완료')

    reservation = models.OneToOneField('reservations.Reservation', on_delete=models.CASCADE,
                                       related_name='status')
    status = models.CharField(choices=ChoiceStatus.choices, default=ChoiceStatus.NOTPAID, max_length=30,
                              help_text='대여진행상태')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)
