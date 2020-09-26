from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from cars.models import Car, CarTimeTable


@admin.register(Car)
class CarAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'number',
                    'name',
                    'zone',
                    'image',
                    'manufacturer',
                    'fuel_type',
                    'type_of_vehicle',
                    'shift_type',
                    'riding_capacity',
                    'is_event_model',
                    'manual_page',
                    'safety_option',
                    'convenience_option',)


@admin.register(CarTimeTable)
class CarTimeTableAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'zone', 'car', 'date_time_start', 'date_time_end')

#
# @admin.register(PhotoBeforeUse)
# class PhotoBeforeUseAdmin(ImportExportMixin, admin.ModelAdmin):
#     list_display = ('id', 'member', 'reservation', 'image', 'time_stamp')
