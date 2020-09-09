from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reservations.models import Reservation
from reservations.serializers import ReservationCreateSerializer


class ReservationCreateViews(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)
