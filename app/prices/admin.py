from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from prices.models import CarPrice, InsuranceFee, Coupon


@admin.register(CarPrice)
class CarPriceAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'car',
                    'standard_price',
                    'min_price_per_km',
                    'mid_price_per_km',
                    'max_price_per_km',
                    'weekday_price_per_ten_min',
                    'weekend_price_per_ten_min')


@admin.register(InsuranceFee)
class InsuranceFeeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'car',
                    'light_price',
                    'standard_price',
                    'special_price',
                    'light_price_per_ten_min',
                    'standard_price_per_ten_min',
                    'special_price_per_ten_min')


@admin.register(Coupon)
class CouponAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'member',
                    'date_time_start',
                    'expire_date_time',
                    'title',
                    'limit_delta_term',
                    'discount_fee',
                    'is_enabled',
                    'will_use_check',
                    'is_used',
                    'is_free',
                    'description',
                    'created_at',
                    'updated_at')
