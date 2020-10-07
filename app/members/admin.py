from django.contrib import admin
from import_export.admin import ImportExportMixin

from members.models import Member, Profile, PhoneAuth


@admin.register(Member)
class MemberAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'email',
                    'password',
                    'phone',)


@admin.register(Profile)
class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'image',
                    'name',
                    'credit_point',)


@admin.register(PhoneAuth)
class PhoneAuthAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'auth_number',
                    'phone_number',
                    'registration_id',)
