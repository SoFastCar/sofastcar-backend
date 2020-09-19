from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def rest_exception_handler(exc, context):
    res = exception_handler(exc, context)

    if res:
        res.data['status'] = res.status_code
        res.data['code'] = getattr(exc, 'code', getattr(exc, 'default_code', None)) or res.data['detail'].code
    return res


class ReservationDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 reservation 인스턴스가 존재하지 않습니다.'
    default_code = 'DoesNotExist'


class CarZoneDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 carzone 인스턴스가 존재하지 않습니다.'
    default_code = 'DoesNotExist'


class CarDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 car 인스턴스가 존재하지 않습니다.'
    default_code = 'DoesNotExist'


class PaymentDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 payment 인스턴스가 존재하지 않습니다.'
    default_code = 'DoesNotExist'


class TooLessOrTooMuchTimeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '최소 30분부터 최대 30일까지 설정 가능합니다.'
    default_code = 'TooLessOrTooMuchTime'


class NotAvailableCarException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '해당 carzone에서 이용가능한 car id가 아닙니다.'
    default_code = 'NotAvailableCar'


class ShortCreditException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '크레딧이 부족합니다.'
    default_code = 'ShortCredit'


class AlreadyReservedTimeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '해당 이용시간대는 사용 불가능합니다.'
    default_code = 'AlreadyReservedTime'


class BeforeTheCurrentTimeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '현재 시간 이후부터 예약 가능합니다.'
    default_code = 'BeforeTheCurrentTime'


class NotValidInsuranceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '가능한 insurance 이름이 아닙니다.'
    default_code = 'NotValidInsurance'
