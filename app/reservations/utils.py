def insurance_price(insurance, from_when, to_when):
    time = (to_when - from_when).total_seconds() / 60

    if insurance == 'special':
        insurance = int(round(6120 * time / 30, -1))
    elif insurance == 'standard':
        insurance = int(round(4370 * time / 30, -1))
    elif insurance == 'light':
        insurance = int(round(3510 * time / 30, -1))
    else:
        insurance = 0
    return insurance


# 기본요금 x 시간(분) / 30 값 반올림
def car_rental_price(standard_price, from_when, to_when):
    time = (to_when - from_when).total_seconds() / 60
    rental_price = int(round(standard_price * time / 30, -2))
    return rental_price
