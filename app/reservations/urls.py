from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews, ReservationTimeUpdateViews, CarReservedTimesViews,
    CarzoneAvailableCarsViews, ReservationCarzoneAvailableCarsViews, ReservationCarUpdateViews
)

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
    path('<int:reservation_id>/insurance/', ReservationInsuranceUpdateViews.as_view()),
    path('<int:reservation_id>/time/', ReservationTimeUpdateViews.as_view()),

    # update할 carzone에서 이용가능한 car 리스트
    path('<int:reservation_id>/carzones/<int:carzone_id>/cars/', ReservationCarzoneAvailableCarsViews.as_view()),
    # car 리스트 중 선택하여 update
    path('<int:reservation_id>/carzones/<int:carzone_id>/car/', ReservationCarUpdateViews.as_view()),

    path('cars/<int:car_id>/times/', CarReservedTimesViews.as_view()),

    # datetime format ex) 2019-10-03T12:34:00.000
    path('carzones/<int:carzone_id>/cars/', CarzoneAvailableCarsViews.as_view()),
]
