# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from cars.serializers import CarSerializer


class CarViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated, ]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(zone=self.kwargs.get('carzone_pk'))
        return super().filter_queryset(queryset)

# class PhotoBeforeUseViewSet(mixins.CreateModelMixin,
#                             GenericViewSet):
#     queryset = PhotoBeforeUse.objects.all()
#     serializer_class = PhotoBeforeUseSerializer
#     permission_classes = [IsAuthenticated, ]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         queryset = queryset.filter(reservation_id=self.kwargs.get('reservation_pk'))
#         return queryset
#
#     def perform_create(self, serializer):
#         reservation = get_object_or_404(Reservation, id=self.kwargs.get('reservation_pk'))
#         serializer.save(member=self.request.user, reservation=reservation)
