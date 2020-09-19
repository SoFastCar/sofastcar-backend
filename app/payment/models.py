from django.db import models

from core.utils import payment_price


class Payment(models.Model):
    distance = models.FloatField(null=True)
    payment_date = models.DateTimeField(auto_now=True)  # update시 자동 갱신

    def miles_credit(self):
        price = self.reservation.car.carprice
        min_price, mid_price, max_price = price.min_price_per_km, price.mid_price_per_km, price.max_price_per_km
        return payment_price(self.distance, min_price, mid_price, max_price)
