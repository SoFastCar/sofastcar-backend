from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews
)

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
    path('<int:pk>/insurance/', ReservationInsuranceUpdateViews.as_view()),
]
