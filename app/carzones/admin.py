from django.contrib import admin

# Register your models here.
from carzones.models import CarZone


@admin.register(CarZone)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'zone_id',
                    'name',
                    'address',
                    'region',
                    'latitude',
                    'longitude',
                    'detail_info',
                    'blog_page',
                    'type',)
