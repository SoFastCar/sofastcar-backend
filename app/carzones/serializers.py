from rest_framework.serializers import ModelSerializer

from .models import CarZone


class CarZoneSerializer(ModelSerializer):
    class Meta:
        model = CarZone
