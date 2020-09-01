from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from cars.models import Car
from prices.models import CarPrice


@admin.register(CarPrice)
class CarPriceAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'car',
                    'standard_price',
                    'min_price_per_km',
                    'mid_price_per_km',
                    'max_price_per_km',)
