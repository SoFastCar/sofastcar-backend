from django.urls import path

from reservations.views import (
    ReservationCreateViews, ReservationInsuranceUpdateViews, ReservationTimeUpdateViews, CarReservedTimesViews,
    CarzoneAvailableCarsViews, ReservationCarzoneAvailableCarsViews, ReservationCarUpdateViews,
    ReservationInsurancePricesViews, ReservationTimeExtensionUpdateViews, ReservationAlarmViews
)

urlpatterns = [
    # carzone별 car 리스트
    # datetime format: YYYYmmddHHMM ex) 202010031530
    path('carzones/<int:carzone_id>/cars/', CarzoneAvailableCarsViews.as_view()),
    # reservation 생성
    path('', ReservationCreateViews.as_view()),

    # update하기 전, 해당 reservation 조건의 면책보험료 리스트
    path('<int:reservation_id>/insurances/', ReservationInsurancePricesViews.as_view()),
    # 면책보험료 리스트 중 선택하여 보험상품 update
    path('<int:reservation_id>/insurance/', ReservationInsuranceUpdateViews.as_view()),

    # 해당 reseravtion의 이용시간 update
    path('<int:reservation_id>/time/', ReservationTimeUpdateViews.as_view()),

    # update할 carzone에서 이용가능한 car 리스트
    path('<int:reservation_id>/carzones/<int:carzone_id>/cars/', ReservationCarzoneAvailableCarsViews.as_view()),
    # car 리스트 중 선택하여 car update
    path('<int:reservation_id>/carzones/<int:carzone_id>/car/', ReservationCarUpdateViews.as_view()),

    # car별 예약된 시간대 리스트
    path('cars/<int:car_id>/times/', CarReservedTimesViews.as_view()),

    # 반납연장 update
    path('<int:reservation_id>/time/extension/', ReservationTimeExtensionUpdateViews.as_view()),

    # 예약 시작 알림 대여정보 및 결제내역
    path('<int:reservation_id>/alarm/', ReservationAlarmViews.as_view()),
]
