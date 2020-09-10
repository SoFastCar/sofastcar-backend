from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class CarZone(models.Model):
    class ChoiceRegion(models.TextChoices):
        SEOUL = 'SEOUL', _('서울')
        GYEONGGI = 'GYENGGI', _('경기도')
        INCHEON = 'INCHEON', _('인천')

    class ChoiceOperatingTime(models.TextChoices):
        A_TIME = '24시간', _('24시간')
        B_TIME = '06:00 ~ 23:59', _('06:00 ~ 23:59')
        C_TIME = '07:00 ~ 23:59', _('07:00 ~ 23:59')
        D_TIME = '05:30 ~ 23:59', _('05:30 ~ 23:59')

    class ChoiceZoneType(models.TextChoices):
        A_TYPE = '지하', _('지하')
        B_TYPE = '지상', _('지상')
        C_TYPE = '기계식', _('기계식')

    address = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=ChoiceRegion.choices,
                              default=ChoiceRegion.SEOUL, help_text='지역')

    # 위도, 경도 (단위: Degree)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    sub_info = models.CharField(max_length=100, default='')
    detail_info = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=10, choices=ChoiceZoneType.choices,
                            default=ChoiceZoneType.B_TYPE, help_text='주차장타입')
    operating_time = models.CharField(max_length=20, choices=ChoiceOperatingTime.choices,
                                      default=ChoiceOperatingTime.A_TIME, help_text='운영시간')
