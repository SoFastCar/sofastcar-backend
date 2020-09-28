from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from payments.models import PaymentBeforeUse, PaymentAfterUse, TollFee


@admin.register(PaymentBeforeUse)
class PaymentBeforeUseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'reservation',
                    'rental_fee',
                    'insurance_fee',
                    'coupon_discount',
                    'etc_discount',
                    'total_fee',
                    'created_at',
                    'updated_at')


@admin.register(PaymentAfterUse)
class PaymentAfterUseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'driving_distance',
                    'first_section_fee',
                    'second_section_fee',
                    'third_section_fee',
                    'total_toll_fee',
                    'total_fee',
                    'created_at',
                    'updated_at')


@admin.register(TollFee)
class TollFeeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'reservation',
                    'toll_gate',
                    'toll_fee',
                    'created_at')
