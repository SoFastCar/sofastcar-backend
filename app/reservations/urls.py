from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews, ReservationTimeUpdateViews, CarReservedTimesViews
)

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
    path('<int:reservation_id>/insurance/', ReservationInsuranceUpdateViews.as_view()),
    path('<int:reservation_id>/time/', ReservationTimeUpdateViews.as_view()),
    path('<int:car_id>/times/', CarReservedTimesViews.as_view()),
]
