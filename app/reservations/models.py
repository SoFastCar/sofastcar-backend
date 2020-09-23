from django.db import models

from cars.models import Car
from core.utils import insurance_price, car_rental_price
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
    from_when = models.DateTimeField()
    to_when = models.DateTimeField()
    is_extended = models.BooleanField(default=False)
    extended_to_when = models.DateTimeField(null=True)
    rental_date = models.DateTimeField(auto_now_add=True)  # update시 갱신 x
    is_finished = models.BooleanField(default=False)  # payment 생성시 True 갱신

    def time(self):
        if self.is_extended:
            time_minutes = (self.extended_to_when - self.from_when).total_seconds() / 60
        elif not self.is_extended:
            time_minutes = (self.to_when - self.from_when).total_seconds() / 60
        return time_minutes

    def rental_standard_credit(self):
        price = car_rental_price(self.car.carprice.standard_price, self.from_when, self.to_when)
        return price

    def rental_insurance_credit(self):
        insurance = insurance_price(self.insurance, self.from_when, self.to_when)
        return insurance

    def rental_credit(self):
        return self.rental_standard_credit() + self.rental_insurance_credit()

    def extended_standard_credit(self):
        if self.is_extended:
            price = car_rental_price(self.car.carprice.standard_price, self.to_when, self.extended_to_when)
            return price
        elif not self.is_extended:
            return 0

    def extended_insurance_credit(self):
        if self.is_extended:
            insurance = insurance_price(self.insurance, self.to_when, self.extended_to_when)
            return insurance
        elif not self.is_extended:
            return 0

    def extended_credit(self):
        return self.extended_standard_credit() + self.extended_insurance_credit()
