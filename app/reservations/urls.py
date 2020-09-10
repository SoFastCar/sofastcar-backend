from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews, ReservationTimeUpdateViews, CarReservedTimesViews,
    CarzoneAvailableCarsViews
)

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
    path('<int:reservation_id>/insurance/', ReservationInsuranceUpdateViews.as_view()),
    path('<int:reservation_id>/time/', ReservationTimeUpdateViews.as_view()),
    path('cars/<int:car_id>/times/', CarReservedTimesViews.as_view()),
    path('carzones/<int:pk>/cars/', CarzoneAvailableCarsViews.as_view()),  # datetime format ex) 2019-10-03T12:34:00.000
    # path('carzones/<int:pk>/cars/detail', CarzoneAvailableCarsDetailViews.as_view()),
]
