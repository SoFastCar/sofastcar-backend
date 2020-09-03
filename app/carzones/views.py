# Create your views here.
from rest_framework.viewsets import ModelViewSet

from .models import CarZone
from .serializers import CarZoneSerializer


class CarZoneViewSet(ModelViewSet):
    queryset = CarZone.objects.all()
    serializer_class = CarZoneSerializer
