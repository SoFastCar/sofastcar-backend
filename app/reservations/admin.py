from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from reservations.models import Reservation, ReservationStatus


@admin.register(Reservation)
class ReservationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'member',
                    'zone',
                    'car',
                    'insurance',
                    'date_time_start',
                    'date_time_end',
                    'date_time_extension',
                    'created_at',
                    'updated_at')


@admin.register(ReservationStatus)
class ReservationStatusAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id',
                    'reservation',
                    'status',
                    'created_at',
                    'updated_at')
