import base64
import datetime
import hashlib
import hmac
import json
import secrets
import time

import requests
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db import models
from django.utils import timezone

from prices.models import Coupon


class MemberManager(BaseUserManager):
    def _create_user(self, name, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, password=password, **extra_fields)
        user.save()
        return user

    def create_user(self, name, email, password, **extra_fields):
        extra_fields.setdefault('is_admin', False)
        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self._create_user(name, email, password, **extra_fields)


class Member(AbstractBaseUser):
    name = models.CharField(max_length=10)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    phone = models.CharField(max_length=11)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """
        Is the user a member of staff?
        """
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def save(self, *args, **kwargs):

        if not self.id:
            self.set_password(self.password)
            super().save(*args, **kwargs)
            Profile.objects.create(member=self)
            Coupon.objects.create(member=self, title='가입 기념 1만원 쿠폰',
                                  expire_date_time=datetime.datetime(2020, 12, 19, 12, 0, tzinfo=datetime.timezone.utc),
                                  discount_fee=10000, date_time_start=timezone.now())
        else:
            super().save(*args, **kwargs)


class Profile(models.Model):
    member = models.OneToOneField('members.Member',
                                  related_name='profile',
                                  on_delete=models.CASCADE,
                                  )
    image = models.ImageField(null=True)
    credit_point = models.PositiveIntegerField(default=5_000_000)



class PhoneAuth(models.Model):
    phone_number = models.CharField(max_length=11)
    registration_id = models.CharField(
        verbose_name='주민등록번호',
        max_length=7,
    )
    auth_number = models.IntegerField()
    ttl = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.auth_number = secrets.choice(range(100000, 999999))
        self.ttl = timezone.now() + datetime.timedelta(minutes=5)
        super().save(*args, **kwargs)

        self.send_sms()

    def send_sms(self):
        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)

        url = "https://sens.apigw.ntruss.com"
        requestUrl1 = "/sms/v2/services/"
        requestUrl2 = "/messages"
        serviceId = "ncp:sms:kr:260483911484:sofastcar_sms"
        access_key = "RcSVHr6YgMHKg38rmR4X"

        uri = requestUrl1 + serviceId + requestUrl2
        apiUrl = url + uri

        secret_key = "7PWFNRn7Md46Dgegpf8MAncOaSPH4ReDICyJf4xZ"
        secret_key = bytes(secret_key, 'UTF-8')
        method = "POST"
        message = method + " " + uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, 'UTF-8')

        signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        messages = {"to": f"{self.phone_number}"}
        body = {
            "type": "SMS",
            "contentType": "COMM",
            "from": "01047340350",
            "subject": "subject",
            "content": f"[인증번호]: {self.auth_number}",
            "messages": [messages]
        }
        body2 = json.dumps(body)

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': access_key,
            'x-ncp-apigw-signature-v2': signingKey
        }

        requests.post(apiUrl, headers=headers, data=body2)
