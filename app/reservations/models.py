from django.db import models
from django.utils.translation import gettext as _


# Create your models here.


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
    date_time_extension = models.DateTimeField(help_text='연장종료날짜시간')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)


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
