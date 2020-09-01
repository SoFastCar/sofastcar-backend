from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MemberManager(BaseUserManager):
    def _create_user(self, email, password, registration_id):
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, registration_id=registration_id)
        user.save()
        return user

    def _create_superuser(self, email, password, registration_id):
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, registration_id=registration_id)
        user.is_admin = True
        user.save()
        return user

    def create_user(self, email, password, registration_id):
        return self._create_user(email, password, registration_id)

    def create_superuser(self, email, password, registration_id):
        return self._create_superuser(email, password, registration_id)


class Member(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    registration_id = models.CharField(
        verbose_name='주민등록번호',
        max_length=7,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['registration_id']

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
        self.set_password(self.password)

        if not self.id:
            super().save(*args, **kwargs)

            registration_id = self.registration_id
            Profile.objects.create(
                member=self,
                birth=f'{registration_id[0:2]}-{registration_id[2:4]}-{registration_id[4:6]}'
            )
        else:
            super().save(*args, **kwargs)


class Profile(models.Model):
    member = models.OneToOneField('members.Member',
                                  related_name='profile',
                                  on_delete=models.CASCADE,
                                  unique=True,
                                  )
    image = models.ImageField(null=True)
    birth = models.CharField(max_length=16)
    credit_point = models.IntegerField(default=0)
