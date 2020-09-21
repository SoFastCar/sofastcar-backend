from django.urls import path

from payment.views import PaymentCreateViews

urlpatterns = [
    path('', PaymentCreateViews.as_view()),
]
