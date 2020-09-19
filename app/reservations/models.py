from django.db import models

from cars.models import Car
from core.utils import insurance_price, car_rental_price, time_format
from members.models import Member
from payment.models import Payment


class Reservation(models.Model):
    class Insurance(models.TextChoices):
        SPECIAL = 'special'
        STANDARD = 'standard'
        LIGHT = 'light'
        NONE = 'none'

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations')
    payment = models.OneToOneField(Payment, null=True, blank=True, on_delete=models.CASCADE, related_name='reservation')
    insurance = models.CharField(choices=Insurance.choices, default=Insurance.NONE, max_length=40)
    from_when = models.CharField(max_length=20)
    to_when = models.CharField(max_length=20)
    is_extended = models.BooleanField(default=False)
    extended_to_when = models.CharField(max_length=20, null=True)
    rental_date = models.DateTimeField(auto_now_add=True)  # update시 갱신 x
    is_finished = models.BooleanField(default=False)  # payment 생성시 True 갱신

    def time(self):
        from_when = time_format(self.from_when)
        to_when = time_format(self.to_when)
        time_minutes = (to_when - from_when).total_seconds() / 60
        return time_minutes

    def rental_credit(self):
        from_when = time_format(self.from_when)
        to_when = time_format(self.to_when)
        price = car_rental_price(self.car.carprice.standard_price, from_when, to_when)
        return price

    def insurance_credit(self):
        from_when = time_format(self.from_when)
        to_when = time_format(self.to_when)
        insurance = insurance_price(self.insurance, from_when, to_when)
        return insurance

    def extended_rental_credit(self):
        if self.is_extended:
            to_when = time_format(self.to_when)
            extended_to_when = time_format(self.extended_to_when)
            price = car_rental_price(self.car.carprice.standard_price, to_when, extended_to_when)
            return price
        elif not self.is_extended:
            return 0

    def extended_insurance_credit(self):
        if self.is_extended:
            to_when = time_format(self.to_when)
            extended_to_when = time_format(self.extended_to_when)
            insurance = insurance_price(self.insurance, to_when, extended_to_when)
            return insurance
        elif not self.is_extended:
            return 0

    def total_credit(self):
        return self.rental_credit() + self.insurance_credit() + self.extended_rental_credit() + self.extended_insurance_credit()
