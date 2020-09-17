from django.db import models

from core.utils import payment_price, car_rental_price, insurance_price


class Payment(models.Model):
    distance = models.FloatField()
    is_time_extended = models.BooleanField(default=False, blank=False)
    extended_to_when = models.DateTimeField(null=True)
    payment_date = models.DateTimeField(auto_now_add=True)  # update시 갱신 x

    def miles_credit(self):
        price = self.reservation.car.carprice
        min_price, mid_price, max_price = price.min_price_per_km, price.mid_price_per_km, price.max_price_per_km
        return payment_price(self.distance, min_price, mid_price, max_price)

    def extended_standard_credit(self):
        if self.is_time_extended:
            standard_price = self.reservation.car.carprice.standard_price
            return car_rental_price(standard_price, self.reservation.to_when, self.extended_to_when)
        elif not self.is_time_extended:
            return 0

    def extended_insurance_credit(self):
        if self.is_time_extended:
            return insurance_price(self.reservation.insurance, self.reservation.to_when, self.extended_to_when)
        elif not self.is_time_extended:
            return 0

    def total_credit(self):
        return self.miles_credit() + self.extended_standard_credit() + self.extended_insurance_credit()
