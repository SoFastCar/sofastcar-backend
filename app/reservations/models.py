from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from cars.models import Car
from members.models import Member


class Payment(models.Model):
    mileage = models.FloatField()

    def payment_credit(self):
        pass


class Reservation(models.Model):
    INSURANCES = (
        ('special', 'special'),
        ('standard', 'standard'),
        ('light', 'light'),
        ('none', 'none'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations')
    payment = models.OneToOneField(Payment, null=True, blank=True, on_delete=models.CASCADE, related_name='reservation')
    insurance = models.CharField(choices=INSURANCES, default='none', max_length=40)
    from_when = models.DateTimeField()
    to_when = models.DateTimeField()
    rental_date = models.DateTimeField(auto_now=True)  # update마다 자동 갱신
    is_finished = models.BooleanField(default=False)  # payment 생성시 True 자동 갱신

    def time(self):
        time_minutes = (self.to_when - self.from_when).total_seconds() / 60
        return time_minutes

    def insurance_credit(self):
        if self.insurance == 'special':
            insurance = int(round(6120 * self.time() / 30, -1))
        elif self.insurance == 'standard':
            insurance = int(round(4370 * self.time() / 30, -1))
        elif self.insurance == 'light':
            insurance = int(round(3510 * self.time() / 30, -1))
        else:
            insurance = 0
        return insurance

    # (기본요금 x 시간(분) / 30 값 반올림) + (보험료)
    def reservation_credit(self):
        return int(round(self.car.carprice.standard_price * self.time() / 30, -2) + self.insurance_credit())


# 결제 인스턴스 생성시 예매 인스턴스에서 is_finished True로 update
@receiver(post_save, sender=Payment)
def reservation_finished(instance, created, **kwargs):
    if created:
        instance.reservation.is_finished = True
        instance.reservation.save()
