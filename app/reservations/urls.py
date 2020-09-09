from django.urls import path

from reservations.views import ReservationCreateViews

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
]