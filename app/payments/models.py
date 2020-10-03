from django.db import models


# Create your models here.
class PaymentBeforeUse(models.Model):
    reservation = models.OneToOneField('reservations.Reservation', on_delete=models.CASCADE,
                                       related_name='payment_before')
    rental_fee = models.PositiveIntegerField(help_text='운행전대여료')
    insurance_fee = models.PositiveIntegerField(help_text='차량손해면책보험료')
    coupon_discount = models.PositiveIntegerField(default=0, help_text='쿠폰할인가격')
    etc_discount = models.PositiveIntegerField(default=0, help_text='기타할인금액')
    extension_fee = models.PositiveIntegerField(default=0, help_text='연장요금')
    total_fee = models.PositiveIntegerField(help_text='총운행전요금')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)


class PaymentAfterUse(models.Model):
    reservation = models.OneToOneField('reservations.Reservation', on_delete=models.CASCADE,
                                       related_name='payment_after')
    driving_distance = models.PositiveIntegerField(help_text='운행거리')
    first_section_fee = models.PositiveIntegerField(help_text='0~30km 구간 주행요금')
    second_section_fee = models.PositiveIntegerField(help_text='31~100km 구간 주행요금')
    third_section_fee = models.PositiveIntegerField(help_text='100km 이후 주행요금')
    total_toll_fee = models.PositiveIntegerField(default=0, help_text='총통행료')
    total_fee = models.PositiveIntegerField(help_text='총운행후요금')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
    updated_at = models.DateTimeField(auto_now=True)


class TollFee(models.Model):
    reservation = models.ForeignKey('reservations.Reservation', on_delete=models.CASCADE,
                                    related_name='toll_fees')
    toll_gate = models.CharField(max_length=30)
    toll_fee = models.PositiveIntegerField(help_text='통행료')
    created_at = models.DateTimeField(auto_now_add=True, help_text='TimeStamp')
