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
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations')
    payment = models.OneToOneField(Payment, null=True, blank=True, on_delete=models.CASCADE, related_name='reservation')
    insurance = models.CharField(choices=INSURANCES, blank=True, max_length=40)
    from_when = models.DateTimeField()
    to_when = models.DateTimeField()
    rental_date = models.DateTimeField(auto_now=True)  # update마다 자동 갱신
    is_finished = models.BooleanField(default=False)  # payment 생성시 True 자동 갱신

    def time(self):
        time_minutes = (self.to_when - self.from_when).total_seconds() / 60
        return time_minutes

    def reservation_credit(self):
        if self.insurance == 'special':
            insurance = 6120
        elif self.insurance == 'standard':
            insurance = 4370
        elif self.insurance == 'light':
            insurance = 3510
        else:
            insurance = 0

        # 기본요금 x 시간(분) / 30 값 반올림 + 보험료
        return int(round(self.car.carprice.standard_price * self.time() / 30, -2) + insurance)


# 예약시 해당 사용자의 크레딧에서 차감
@receiver(post_save, sender=Reservation)
def deduct_credit(instance, created, **kwargs):
    if created:
        instance.member.profile.credit_point -= instance.reservation_credit()
        instance.member.profile.save()
        return f'보유 크레딧에서 요금이 {instance.reservation_credit()} 차감되었습니다.'


# 결제 인스턴스 생성시 예매 인스턴스에서 is_finished True로 update
@receiver(post_save, sender=Payment)
def reservation_finished(instance, created, **kwargs):
    if created:
        instance.reservation.is_finished = True
        instance.reservation.save()
