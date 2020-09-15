from django.utils.translation import gettext as _
from django.db import models


# Create your models here.
class Car(models.Model):
    class ChoiceManufacturer(models.TextChoices):
        HYUNDAI = '현대자동차', _('현대자동차')
        KIA = '기아자동차', _('기아자동차')
        BMW = 'BMW', _('BMW')
        SSANGYONG = '쌍용자동차', _('쌍용자동차')
        RNAULTSAMSUNG = '르노삼성자동차', _('르노삼성자동차')
        BENZ = '벤츠', _('벤츠')
        PORSCHE = '포르쉐', _('포르쉐')
        CHEVROLET = '쉐보레', _('쉐보레')

    class ChoiceFuelType(models.TextChoices):
        DIESEL = '경유', _('경유')
        GASOLINE = '휘발유', _('휘발유')
        ELECTRIC = '전기', _('전기')

    class ChoiceSizeType(models.TextChoices):
        A_SEGMENT = '경차', _('경차')
        B_SEGMENT = '소형', _('소형')
        C_SEGMENT = '준중형', _('준중형')
        D_SEGMENT = '중형', _('중형')
        E_SEGMENT = '준대형', _('준대형')
        F_SEGMENT = '대형', _('대형')
        S_SEGMENT = '스포츠카', _('스포츠카')
        M_SEGMENT = '미니밴', _('미니밴')
        J_SEGMENT = 'SUV', _('SUV')

    class ChoiceShiftType(models.TextChoices):
        AUTO = '자동', _('자동')
        STICK = '수동', _('수동')

    number = models.CharField(max_length=20, unique=True, help_text='차 번호판')
    name = models.CharField(max_length=30)
    zone = models.ForeignKey('carzones.CarZone', related_name='cars', on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to='CarImages/')
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
    reservation = models.ForeignKey('reservations.Reservation', related_name='ready_photos', on_delete=models.CASCADE)
    member = models.ForeignKey('members.Member', related_name='image_owners', on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=f'ImagesBeforeUse/%Y/%m/%d/{reservation}/')
    time_stamp = models.DateTimeField(auto_now_add=True)
