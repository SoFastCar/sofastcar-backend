from django.utils.translation import gettext as _
from django.db import models


# Create your models here.
class Car(models.Model):
    class ChoiceManufacturer(models.TextChoices):
        HYUNDAI = 'HD', _('현대자동차')
        KIA = 'KIA', _('기아자동차')
        BMW = 'BMW', _('BMW')
        SSANGYONG = 'SSY', _('쌍용자동차')
        RenaultSamsung = 'RS', _('르노삼성자동차')
        BENZ = 'BENZ', _('벤츠')
        PORSCHE = 'POR', _('포르쉐')

    class ChoiceFuelType(models.TextChoices):
        DIESEL = 'DS', _('경유')
        GASOLINE = 'GAS', _('휘발유')
        ELECTRIC = 'ELC', _('전기')

    class ChoiceSizeType(models.TextChoices):
        A_SEGMENT = 'A', _('경차')
        B_SEGMENT = 'B', _('소형')
        C_SEGMENT = 'C', _('준중형')
        D_SEGMENT = 'D', _('중형')
        E_SEGMENT = 'E', _('준대형')
        F_SEGMENT = 'F', _('대형')
        S_SEGMENT = 'S', _('스포츠카')
        M_SEGMENT = 'M', _('미니밴')
        J_SEGMENT = 'J', _('SUV')

    class ChoiceShiftType(models.TextChoices):
        AUTO = 'AT', _('자동')
        STICK = 'MT', _('수동')

    number = models.CharField(max_length=20, unique=True, help_text='차 번호판')
    name = models.CharField(max_length=30)
    zone = models.ForeignKey('carzones.CarZone', related_name='cars', on_delete=models.CASCADE)
    image = models.ImageField(null=True)
    manufacturer = models.CharField(max_length=20, choices=ChoiceManufacturer.choices)
    fuel_type = models.CharField(max_length=20, choices=ChoiceFuelType.choices,
                                 default=ChoiceFuelType.GASOLINE, help_text='연료')
    type_of_vehicle = models.CharField(max_length=10, choices=ChoiceSizeType.choices,
                                       default=ChoiceSizeType.C_SEGMENT, help_text='차종')
    shift_type = models.CharField(max_length=10, choices=ChoiceShiftType.choices,
                                  default=ChoiceShiftType.AUTO, help_text='기어')
    riding_capacity = models.PositiveIntegerField(help_text='승차정원')
    is_event_model = models.BooleanField(help_text='쏘카세이브')
    manual_page = models.CharField(max_length=100, default='')
    safety_option = models.CharField(max_length=255, default='')
    convenience_option = models.CharField(max_length=255, default='')


class PhotoBeforeUse(models.Model):
    # 예약 완료 건 FK 추가 필요
    member = models.ForeignKey('members.Member', related_name='image_owners', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ImagesBeforeUse/%Y/%m/%d')
    time_stamp = models.DateTimeField(auto_now_add=True)
