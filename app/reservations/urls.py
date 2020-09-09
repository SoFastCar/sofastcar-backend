from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews, ReservationTimeUpdateViews
)

urlpatterns = [
    path('', ReservationCreateViews.as_view()),
    path('<int:pk>/insurance/', ReservationInsuranceUpdateViews.as_view()),
    path('<int:pk>/time/', ReservationTimeUpdateViews.as_view()),
]
