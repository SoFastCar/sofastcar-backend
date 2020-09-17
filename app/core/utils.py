from reservations.exceptions import NotValidInsuranceException


def insurance_price(insurance, from_when, to_when):
    time = (to_when - from_when).total_seconds() / 60

    if insurance == 'special':
        insurance = int(round(6120 * time / 30, -1))
    elif insurance == 'standard':
        insurance = int(round(4370 * time / 30, -1))
    elif insurance == 'light':
        insurance = int(round(3510 * time / 30, -1))
    elif insurance == 'none':
        insurance = 0
    else:
        raise NotValidInsuranceException
    return insurance


# 예약시 결제 요금 = 기본요금 x 시간(분) / 30 값 반올림
def car_rental_price(standard_price, from_when, to_when):
    time = (to_when - from_when).total_seconds() / 60
    rental_price = int(round(standard_price * time / 30, -2))
    return rental_price


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
