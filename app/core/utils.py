import datetime

import pytz

from core.exceptions import NotValidInsuranceException, NotValidTimeFormatException, NotInTenMinutesException

KST = pytz.timezone('Asia/Seoul')


# 주행거리에 따른 반납 결제 요금
def payment_price(distance, min_price, mid_price, max_price):
    price = 0

    if distance >= 30:
        price += (max_price * 30)
        distance -= 30
    else:
        price += (max_price * distance)
        return int(round(price, -1))

    if distance >= 70:
        price += (mid_price * 70)
        distance -= 70
    else:
        price += (mid_price * distance)
        return int(round(price, -1))

    if distance >= 0:
        price += (min_price * distance)
        return int(round(price, -1))


def time_format(datetime_str):
    if not (type(datetime_str) == str and len(datetime_str) == 12):
        raise NotValidTimeFormatException

    year, month, day, hour, minute = int(datetime_str[:4]), int(datetime_str[4:6]), int(datetime_str[6:8]), int(
        datetime_str[8:10]), int(datetime_str[10:])

    if str(minute)[-1] != '0':
        raise NotInTenMinutesException
    datetime_format = datetime.datetime(year, month, day, hour, minute)
    utc_datetime = datetime_format - datetime.timedelta(hours=9)
    utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)

    return utc_datetime


def trans_kst_to_utc(iso_datetime_str):
    datetime_format = datetime.datetime.fromisoformat(iso_datetime_str)
    utc_datetime = datetime_format - datetime.timedelta(hours=9)
    utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)
    return datetime.datetime.isoformat(utc_datetime)

# date_time_start YYYY-MM-DDT15:00:00 (UTC) == YYYY-MM-DDT00:00:00 (KST)
def get_only_date_from_datetime(datetime_format):
    only_date = datetime_format.replace(hour=15, minute=0, second=0)
    return only_date

# date_time_end YYYY-MM-DDT14:59:59 (UTC) == YYYY-MM-DDT23:59:59 (KST)
def get_only_date_end_from_datetime(datetime_format):
    only_date = datetime_format.replace(hour=14, minute=59, second=59)
    return only_date
