from rest_framework.serializers import ModelSerializer

from events.models import EventPhoto


class EventPhotoListSerializer(ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = ['id', 'name', 'image']
        read_only_fields = ('id', 'name', 'image')