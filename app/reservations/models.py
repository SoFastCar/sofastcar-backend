from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class Reservation(models.Model):
    class ChoiceInsuranceType(models.TextChoices):
        SPECIAL = 'special', _('스페셜')
        STANDARD = 'standard', _('스탠다드')
        LIGHT = 'light', _('라이트')

    class ChoiceStatus(models.TextChoices):
        NOTPAID = 'not_paid', _('결제전')
        PAID = 'paid', _('결제완료')
        USING = 'using', _('사용중')
        EXTENDED = 'extended', _('추가연장')
        FINISHED = 'finished', _('반납완료')

    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='reservations')
    zone = models.ForeignKey('carzones.CarZone', on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='reservations')
    insurance = models.CharField(choices=ChoiceInsuranceType.choices.label, default=ChoiceInsuranceType.LIGHT,
                                 help_text='차량손해면책상품')
    date_start = models.DateTimeField(help_text='예약시작날짜시간')
    date_end = models.DateTimeField(help_text='예약종료날짜시간')
    date_extension = models.DateTimeField(default=date_end, help_text='연장종료날짜시간')
    status = models.CharField(choices=ChoiceStatus.choices.label, default=ChoiceStatus.NOTPAID, help_text='대여진행상태')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)
