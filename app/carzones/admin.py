from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from carzones.models import CarZone


@admin.register(CarZone)
class CarZoneAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'zone_id',
                    'name',
                    'address',
                    'region',
                    'latitude',
                    'longitude',
                    'sub_info',
                    'detail_info',
                    'type',
                    'operating_time',)
