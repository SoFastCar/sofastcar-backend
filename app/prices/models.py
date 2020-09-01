from django.db import models


# Create your models here.
class CarPrice(models.Model):
    car = models.OneToOneField('cars.Car', on_delete=models.CASCADE)
    standard_price = models.PositiveIntegerField(default=0)
    min_price_per_km = models.PositiveIntegerField(default=0)
    mid_price_per_km = models.PositiveIntegerField(default=0)
    max_price_per_km = models.PositiveIntegerField(default=0)
