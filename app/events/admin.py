from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportMixin

from events.models import EventPhoto


@admin.register(EventPhoto)
class CarZoneAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id','name', 'image')
