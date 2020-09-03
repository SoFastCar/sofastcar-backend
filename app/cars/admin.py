from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from cars.models import Car


@admin.register(Car)
class CarAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'number',
                    'name',
                    'zone',
                    'image',
                    'manufacturer',
                    'fuel',
                    'type',
                    'shift_type',
                    'riding_capacity',
                    'is_event_model',
                    'manual_page',
                    'safety_option',
                    'convenience_option',)
