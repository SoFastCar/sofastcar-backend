from django.db import models


# Create your models here.
class CarPrice(models.Model):
    car = models.OneToOneField('cars.Car', related_name='carprice', on_delete=models.CASCADE)
    standard_price = models.PositiveIntegerField(default=0)
    min_price_per_km = models.PositiveIntegerField(default=0)
    mid_price_per_km = models.PositiveIntegerField(default=0)
    max_price_per_km = models.PositiveIntegerField(default=0)


# 차종 상관없이 이용시간별로 보험료 계산
class InsurancePrice(models.Model):
    special = models.PositiveIntegerField(default=6120)
    standard = models.PositiveIntegerField(default=4370)
    light = models.PositiveIntegerField(default=3510)
