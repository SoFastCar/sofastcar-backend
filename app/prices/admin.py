from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from prices.models import CarPrice, InsuranceFee


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
