from django.db import models


# Create your models here.
class Car(models.Model):
    number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=30)
    zone = models.ForeignKey('carzones.CarZone', related_name='socar_zones', on_delete=models.CASCADE)
    image = models.ImageField(null=True)
    manufacturer = models.CharField(max_length=20)
    fuel = models.CharField(max_length=20)
    type = models.CharField(max_length=10)
    shift_type = models.CharField(max_length=10)
    riding_capacity = models.PositiveIntegerField()
    is_event_model = models.BooleanField()
    manual_page = models.CharField(max_length=100, default='')
    safety_option = models.CharField(max_length=255, default='')
    convenience_option = models.CharField(max_length=255, default='')
