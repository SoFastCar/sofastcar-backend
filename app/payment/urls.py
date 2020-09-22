from django.urls import path

from payment.views import PaymentCreateViews, PaymentRentalHistoryViews

urlpatterns = [
    # 반납 결제
    path('', PaymentCreateViews.as_view()),
    # 결제 내역
    path('<int:payment_id>/history/', PaymentRentalHistoryViews.as_view()),
]
