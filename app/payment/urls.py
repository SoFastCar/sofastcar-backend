from django.urls import path

from payment.views import PaymentCreateViews, PaymentRentalHistoryViews

urlpatterns = [
    path('', PaymentCreateViews.as_view()),

    # 예약 시작 알림 대여정보 및 결제내역
    path('<int:payment_id>/history/', PaymentRentalHistoryViews.as_view()),
]
