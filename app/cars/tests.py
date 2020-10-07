import datetime
import io

from PIL import Image

# Create your tests here.
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

# from cars.models import PhotoBeforeUse
from cars.models import CarTimeTable
from core.utils import trans_kst_to_utc, KST
from members.models import Member, Profile
from payments.models import PaymentBeforeUse, PaymentAfterUse
from prices.models import InsuranceFee, Coupon
from reservations.models import ReservationStatus, Reservation, PhotoBeforeUse


class ImageMaker:
    @staticmethod
    def temporary_image(name='test.jpg'):
        file = io.BytesIO()
        image = Image.new('RGB', (1, 1))
        image.save(file, 'jpeg')
        file.name = name
        file.seek(0)
        return file


class CarTestCase(APITestCase):
    def setUp(self):
        self.user = Member.objects.create(email='test@example.com',
                                          name='test',
                                          phone='01033332222',
                                          password='test')
        self.test_image = ImageMaker.temporary_image()
        self.zones = baker.make('carzones.CarZone', _quantity=2)
        self.cars = baker.make('cars.Car', zone=self.zones[0],
                               image=self.test_image.name, _quantity=2)
        # 테스트용 차량 가격 2개
        self.car_price_1 = baker.make('prices.CarPrice',
                                      car=self.cars[0],
                                      standard_price=50000,
                                      weekday_price_per_ten_min=10,
                                      min_price_per_km=10,
                                      mid_price_per_km=100,
                                      max_price_per_km=1000)
        self.car_price_2 = baker.make('prices.CarPrice',
                                      car=self.cars[1],
                                      standard_price=2000,
                                      weekday_price_per_ten_min=20,
                                      min_price_per_km=20,
                                      mid_price_per_km=200,
                                      max_price_per_km=2000)
        self.car_prices = [self.car_price_1, self.car_price_2]

        # 테스트용 차량 스케쥴 2개
        self.schedule_1 = CarTimeTable.objects.create(car_id=self.cars[0].id, zone_id=self.zones[0].id,
                                                      date_time_start='2020-09-26T16:00:00+00:00',
                                                      date_time_end='2020-09-26T18:30:00+00:00')
        self.schedule_2 = CarTimeTable.objects.create(car_id=self.cars[0].id, zone_id=self.zones[0].id,
                                                      date_time_start='2020-09-27T16:00:00+00:00',
                                                      date_time_end='2020-09-27T19:00:00+00:00')
        self.schedules = [self.schedule_1, self.schedule_2]

        # 테스트용 차량 보험료 2개
        self.insurance_1 = InsuranceFee.objects.create(car_id=self.cars[0].id,
                                                       light_price=100, light_price_per_ten_min=10,
                                                       standard_price=200, standard_price_per_ten_min=20,
                                                       special_price=300, special_price_per_ten_min=30)
        self.insurance_2 = InsuranceFee.objects.create(car_id=self.cars[1].id,
                                                       light_price=10, light_price_per_ten_min=1,
                                                       standard_price=20, standard_price_per_ten_min=2,
                                                       special_price=30, special_price_per_ten_min=3)
        self.insurances = [self.insurance_1, self.insurance_2]

        # 테스트용 예약 생성
        self.expected_insurance = 'special'
        self.test_date_time_start = datetime.datetime(2020, 10, 19, 12, 0, tzinfo=datetime.timezone.utc)
        self.test_date_time_end = datetime.datetime(2020, 10, 19, 13, 0, tzinfo=datetime.timezone.utc)
        self.reservation = Reservation.objects.create(car_id=self.cars[0].id,
                                                      zone_id=self.zones[0].id,
                                                      member_id=self.user.id,
                                                      insurance=self.expected_insurance,
                                                      date_time_start=self.test_date_time_start,
                                                      date_time_end=self.test_date_time_end)

        self.coupon_expire_date_time = datetime.datetime(2020, 12, 19, 12, 0, tzinfo=datetime.timezone.utc)
        self.client.force_authenticate(user=self.user)

    def test_should_list_Cars_and_CarPrices(self):
        """
        Request : GET - /carzones/123/cars?date_time_start=202009261400&date_time_end=202009261440
        """
        response = self.client.get(
            f'/carzones/{self.zones[0].id}/cars?date_time_start=202009261400&date_time_end=202009261440')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for entry, response_entry in zip(self.cars, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.name, response_entry['name'])
            self.assertEqual(entry.zone.id, response_entry['zone'])
            self.assertTrue(response_entry['image'].endswith(entry.image.url))
            self.assertEqual(entry.manufacturer, response_entry['manufacturer'])
            self.assertEqual(entry.fuel_type, response_entry['fuel_type'])
            self.assertEqual(entry.type_of_vehicle, response_entry['type_of_vehicle'])
            self.assertEqual(entry.shift_type, response_entry['shift_type'])
            self.assertEqual(entry.riding_capacity, response_entry['riding_capacity'])
            self.assertEqual(entry.is_event_model, response_entry['is_event_model'])
            self.assertEqual(entry.manual_page, response_entry['manual_page'])
            self.assertEqual(entry.safety_option, response_entry['safety_option'])
            self.assertEqual(entry.convenience_option, response_entry['convenience_option'])
            # 입력한 기간에 따른 가격
            self.assertEqual(entry.carprice.standard_price + entry.carprice.weekday_price_per_ten_min,
                             response_entry['term_price'])
            self.assertEqual(entry.insurances.light_price + entry.insurances.light_price_per_ten_min,
                             response_entry['insurance_prices']['light'])
            self.assertEqual(entry.insurances.standard_price + entry.insurances.standard_price_per_ten_min,
                             response_entry['insurance_prices']['standard'])
            self.assertEqual(entry.insurances.special_price + entry.insurances.special_price_per_ten_min,
                             response_entry['insurance_prices']['special'])

        # Car_Prices 부분
        for entry, response_entry in zip(self.car_prices, response.data['results']):
            self.assertEqual(entry.id, response_entry['car_prices']['id'])
            self.assertEqual(entry.car_id, response_entry['car_prices']['car'])
            self.assertEqual(entry.standard_price, response_entry['car_prices']['standard_price'])
            self.assertEqual(entry.min_price_per_km, response_entry['car_prices']['min_price_per_km'])
            self.assertEqual(entry.mid_price_per_km, response_entry['car_prices']['mid_price_per_km'])
            self.assertEqual(entry.max_price_per_km, response_entry['car_prices']['max_price_per_km'])

    def test_should_retrieve_Cars_and_CarPrices(self):
        """
        Request : GET - /carzones/123/cars/456??date_time_start=202009261400&date_time_end=202009261440
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}?date_time_start'
                                   f'=202009261400&date_time_end=202009261440')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(self.cars[0].id, response.data['id'])
        self.assertEqual(self.cars[0].name, response.data['name'])
        self.assertEqual(self.cars[0].zone.id, response.data['zone'])
        self.assertTrue(response.data['image'].endswith(self.cars[0].image.url))
        self.assertEqual(self.cars[0].manufacturer, response.data['manufacturer'])
        self.assertEqual(self.cars[0].fuel_type, response.data['fuel_type'])
        self.assertEqual(self.cars[0].type_of_vehicle, response.data['type_of_vehicle'])
        self.assertEqual(self.cars[0].shift_type, response.data['shift_type'])
        self.assertEqual(self.cars[0].riding_capacity, response.data['riding_capacity'])
        self.assertEqual(self.cars[0].is_event_model, response.data['is_event_model'])
        self.assertEqual(self.cars[0].manual_page, response.data['manual_page'])
        self.assertEqual(self.cars[0].safety_option, response.data['safety_option'])
        self.assertEqual(self.cars[0].convenience_option, response.data['convenience_option'])
        self.assertEqual(self.car_price_1.id, response.data['car_prices']['id'])
        self.assertEqual(self.car_price_1.car_id, response.data['car_prices']['car'])
        self.assertEqual(self.car_price_1.standard_price, response.data['car_prices']['standard_price'])
        self.assertEqual(self.car_price_1.min_price_per_km, response.data['car_prices']['min_price_per_km'])
        self.assertEqual(self.car_price_1.mid_price_per_km, response.data['car_prices']['mid_price_per_km'])
        self.assertEqual(self.car_price_1.max_price_per_km, response.data['car_prices']['max_price_per_km'])
        # 입력한 기간에 따른 가격
        self.assertEqual(self.cars[0].carprice.standard_price + self.cars[0].carprice.weekday_price_per_ten_min,
                         response.data['term_price'])
        self.assertEqual(self.cars[0].insurances.light_price + self.cars[0].insurances.light_price_per_ten_min,
                         response.data['insurance_prices']['light'])
        self.assertEqual(self.cars[0].insurances.standard_price + self.cars[0].insurances.standard_price_per_ten_min,
                         response.data['insurance_prices']['standard'])
        self.assertEqual(self.cars[0].insurances.special_price + self.cars[0].insurances.special_price_per_ten_min,
                         response.data['insurance_prices']['special'])

    def test_should_list_Cars_info_at_selected_CarZone(self):
        """
        Request : GET - /carzones/123/info
        """
        response = self.client.get(
            f'/carzones/{self.zones[0].id}/info?date_time_start=202009261400&date_time_end=202009261440')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response)
        # 시간 반영 요금 정보
        for entry, response_entry in zip(self.car_prices, response.data['cars']):
            # 40분 요금 계산 : standard_price + weekday_price_per_ten_min
            pay = entry.standard_price + entry.weekday_price_per_ten_min
            self.assertEqual(pay, response_entry['term_price'])

        # 차량 정보
        for entry, response_entry in zip(self.cars, response.data['cars']):
            self.assertTrue(response_entry['image'].endswith(entry.image.url))
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.name, response_entry['name'])
            self.assertEqual(entry.is_event_model, response_entry['is_event_model'])

        # 쏘카존 정보
        self.assertEqual(self.zones[0].id, response.data['id'])
        self.assertEqual(self.zones[0].name, response.data['name'])
        self.assertEqual(self.zones[0].sub_info, response.data['sub_info'])
        self.assertEqual(self.zones[0].type, response.data['type'])

        # 보험료 정보
        for entry, response_entry in zip(self.insurances, response.data['cars']):
            # 40분 해당되는 보험료 계산 검사
            light = entry.light_price + entry.light_price_per_ten_min
            standard = entry.standard_price + entry.standard_price_per_ten_min
            special = entry.special_price + entry.special_price_per_ten_min
            self.assertEqual(light, response_entry['insurance_prices']['light'])
            self.assertEqual(standard, response_entry['insurance_prices']['standard'])
            self.assertEqual(special, response_entry['insurance_prices']['special'])

        # time_table 검사
        for entry, response_entry in zip(self.schedules, response.data['time_tables']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.zone_id, response_entry['zone'])
            self.assertEqual(entry.car_id, response_entry['car'])
            self.assertEqual(entry.date_time_start, trans_kst_to_utc(response_entry['date_time_start']))
            self.assertEqual(entry.date_time_end, trans_kst_to_utc(response_entry['date_time_end']))

    def test_should_create_Reservation(self):
        """
        Request : POST - /carzones/123/cars/456/reservations
        """
        expected_status = ReservationStatus.ChoiceStatus.PAID_1.value
        # Credit 초기화
        default_credit = 100000
        self.user.profile.credit_point = default_credit
        self.user.profile.save()

        # 미래 시간으로 data 테스트
        data = {'date_time_start': '2020-10-19T13:10:00Z',
                'date_time_end': '2020-10-19T13:50:00Z',
                'insurance': 'light'}

        response = self.client.post(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}/reservations', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(str(self.zones[0].id), response.data['zone'])
        self.assertEqual(str(self.cars[0].id), response.data['car'])
        self.assertEqual(data['insurance'], response.data['insurance'])
        self.assertEqual(data['date_time_start'], response.data['date_time_start'])
        self.assertEqual(data['date_time_end'], response.data['date_time_end'])
        # Status Check
        self.assertTrue(ReservationStatus.objects.filter(reservation_id=response.data['id']).exists())
        self.assertEqual(expected_status,
                         ReservationStatus.objects.get(reservation_id=response.data['id']).status)
        # Payment Check
        self.assertTrue(PaymentBeforeUse.objects.filter(reservation_id=response.data['id']).exists())
        rental_fee = self.car_price_1.standard_price + self.car_price_1.weekday_price_per_ten_min
        insurance_fee = self.insurance_1.light_price + self.insurance_1.light_price_per_ten_min
        self.assertEqual(rental_fee, PaymentBeforeUse.objects.get(reservation_id=response.data['id']).rental_fee)
        self.assertEqual(insurance_fee, PaymentBeforeUse.objects.get(reservation_id=response.data['id']).insurance_fee)
        self.assertEqual(rental_fee + insurance_fee,
                         PaymentBeforeUse.objects.get(reservation_id=response.data['id']).total_fee)
        # Credit Check
        self.assertEqual(default_credit - rental_fee - insurance_fee,
                         Profile.objects.get(member_id=self.user.id).credit_point)

    def test_should_retrieve_Reservation(self):
        """
        Request : GET - /reservations/123
        """

        response = self.client.get(f'/reservations/{self.reservation.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.zones[0].id, response.data['zone'])
        self.assertEqual(self.cars[0].id, response.data['car'])
        self.assertEqual(self.expected_insurance, response.data['insurance'])
        self.assertEqual(str(self.test_date_time_start.astimezone(KST)).replace(' ', 'T'),
                         response.data['date_time_start'])
        self.assertEqual(str(self.test_date_time_end.astimezone(KST)).replace(' ', 'T'), response.data['date_time_end'])

    def test_should_list_Reservations_owner_only(self):
        """
        Request : GET - /reservations
        """
        user2 = Member.objects.create(email='test2@example.com',
                                      password='test2')
        reservations_user = baker.make('reservations.Reservation',
                                       member=self.user,
                                       car_id=self.cars[0].id,
                                       zone_id=self.zones[0].id,
                                       _quantity=2)
        reservations_user2 = baker.make('reservations.Reservation',
                                        member=user2,
                                        car_id=self.cars[0].id,
                                        zone_id=self.zones[0].id,
                                        _quantity=2)
        self.client.force_authenticate(user=user2)
        response = self.client.get(f'/reservations')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry, response_entry in zip(reservations_user2, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.member.id, response_entry['member'])
            self.assertEqual(entry.car.id, response_entry['car'])
            self.assertEqual(entry.zone.id, response_entry['zone'])
            self.assertEqual(entry.insurance, response_entry['insurance'])
            self.assertEqual(str(entry.date_time_start.astimezone(KST)).replace(' ', 'T'),
                             response_entry['date_time_start'])
            self.assertEqual(str(entry.date_time_end.astimezone(KST)).replace(' ', 'T'),
                             response_entry['date_time_end'])

    def test_should_retrieve_PaymentBeforeUse(self):
        """
            Request : GET - /reservations/123/payment_before
        """
        response = self.client.get(f'/reservations/{self.reservation.id}/payment_before')

        entry = PaymentBeforeUse.objects.get(reservation_id=self.reservation.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(entry.id, response.data['results'][0]['id'])
        self.assertEqual(entry.member.id, response.data['results'][0]['member'])
        self.assertEqual(entry.reservation.id, response.data['results'][0]['reservation'])
        self.assertEqual(entry.rental_fee, response.data['results'][0]['rental_fee'])
        self.assertEqual(entry.insurance_fee, response.data['results'][0]['insurance_fee'])
        self.assertEqual(entry.coupon_discount, response.data['results'][0]['coupon_discount'])
        self.assertEqual(entry.etc_discount, response.data['results'][0]['etc_discount'])
        self.assertEqual(entry.extension_fee, response.data['results'][0]['extension_fee'])
        self.assertEqual(entry.total_fee, response.data['results'][0]['total_fee'])

    def test_should_create_PaymentAfterUse_gte_100_distance(self):
        """
            Request : POST - /reservations/123/payment_after
            주행거리 100 Km 이상 구간 테스트
        """
        # Credit 초기화
        default_credit = 100000
        self.user.profile.credit_point = default_credit
        self.user.profile.save()

        data = {'driving_distance': '120'}
        distance = int(data['driving_distance'])
        first_section_fee = (distance - 100) * self.car_price_1.min_price_per_km
        second_section_fee = 70 * self.car_price_1.mid_price_per_km
        third_section_fee = 30 * self.car_price_1.max_price_per_km
        total_fee = first_section_fee + second_section_fee + third_section_fee

        response = self.client.post(f'/reservations/{self.reservation.id}/payment_after', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(first_section_fee, response.data['first_section_fee'])
        self.assertEqual(second_section_fee, response.data['second_section_fee'])
        self.assertEqual(third_section_fee, response.data['third_section_fee'])
        self.assertEqual(total_fee, response.data['total_fee'])
        self.assertEqual(self.user.id, response.data['member'])
        self.assertEqual(str(self.reservation.id), response.data['reservation'])
        self.assertEqual(distance, response.data['driving_distance'])

        # Credit Check
        self.assertEqual(default_credit - total_fee,
                         Profile.objects.get(member_id=self.user.id).credit_point)

    def test_should_create_PaymentAfterUse_gte_70_lte_100_distance(self):
        """
            Request : POST - /reservations/123/payment_after
            주행거리 30 Km 이상 100 Km 이하 구간 테스트
        """
        # Credit 초기화
        default_credit = 100000
        self.user.profile.credit_point = default_credit
        self.user.profile.save()

        data = {'driving_distance': '90'}
        distance = int(data['driving_distance'])
        first_section_fee = 0
        second_section_fee = (distance - 70) * self.car_price_1.mid_price_per_km
        third_section_fee = 30 * self.car_price_1.max_price_per_km
        total_fee = first_section_fee + second_section_fee + third_section_fee

        response = self.client.post(f'/reservations/{self.reservation.id}/payment_after', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(first_section_fee, response.data['first_section_fee'])
        self.assertEqual(second_section_fee, response.data['second_section_fee'])
        self.assertEqual(third_section_fee, response.data['third_section_fee'])
        self.assertEqual(total_fee, response.data['total_fee'])
        self.assertEqual(self.user.id, response.data['member'])
        self.assertEqual(str(self.reservation.id), response.data['reservation'])
        self.assertEqual(distance, response.data['driving_distance'])

        # Credit Check
        self.assertEqual(default_credit - total_fee,
                         Profile.objects.get(member_id=self.user.id).credit_point)

    def test_should_create_PaymentAfterUse_lte_30_distance(self):
        """
            Request : POST - /reservations/123/payment_after
            주행거리 30 Km 이하 구간 테스트
        """

        # Credit 초기화
        default_credit = 100000
        self.user.profile.credit_point = default_credit
        self.user.profile.save()

        data = {'driving_distance': '20'}
        distance = int(data['driving_distance'])
        first_section_fee = 0
        second_section_fee = 0
        third_section_fee = distance * self.car_price_1.max_price_per_km
        total_fee = first_section_fee + second_section_fee + third_section_fee

        response = self.client.post(f'/reservations/{self.reservation.id}/payment_after', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(first_section_fee, response.data['first_section_fee'])
        self.assertEqual(second_section_fee, response.data['second_section_fee'])
        self.assertEqual(third_section_fee, response.data['third_section_fee'])
        self.assertEqual(total_fee, response.data['total_fee'])
        self.assertEqual(self.user.id, response.data['member'])
        self.assertEqual(str(self.reservation.id), response.data['reservation'])
        self.assertEqual(distance, response.data['driving_distance'])

        # Credit Check
        self.assertEqual(default_credit - total_fee,
                         Profile.objects.get(member_id=self.user.id).credit_point)

    def test_should_retrieve_PaymentAfterUse(self):
        """
            Request : GET - /reservations/123/payment_after
        """
        entry = PaymentAfterUse.objects.create(driving_distance=100,
                                               first_section_fee=10,
                                               second_section_fee=100,
                                               third_section_fee=1000,
                                               total_fee=1110,
                                               member_id=self.user.id,
                                               reservation_id=self.reservation.id)
        response = self.client.get(f'/reservations/{self.reservation.id}/payment_after')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(entry.id, response.data['results'][0]['id'])
        self.assertEqual(entry.first_section_fee, response.data['results'][0]['first_section_fee'])
        self.assertEqual(entry.second_section_fee, response.data['results'][0]['second_section_fee'])
        self.assertEqual(entry.third_section_fee, response.data['results'][0]['third_section_fee'])
        self.assertEqual(entry.total_fee, response.data['results'][0]['total_fee'])
        self.assertEqual(entry.member.id, response.data['results'][0]['member'])
        self.assertEqual(entry.reservation.id, response.data['results'][0]['reservation'])

    def test_should_list_UseHistory(self):
        """
            Request : GET - /reservations/history
        """
        expected_status = '반납완료'
        user2 = Member.objects.create(email='test2@example.com',
                                      password='test2')
        self.client.force_authenticate(user=user2)
        reservations = baker.make('reservations.Reservation',
                                  member=user2,
                                  car_id=self.cars[0].id,
                                  zone_id=self.zones[0].id,
                                  _quantity=2)
        payment_1 = baker.make('payments.PaymentAfterUse',
                               member=user2,
                               reservation_id=reservations[0].id,
                               driving_distance=100,
                               first_section_fee=10,
                               second_section_fee=100,
                               third_section_fee=1000,
                               total_fee=1110)
        payment_2 = baker.make('payments.PaymentAfterUse',
                               member=user2,
                               reservation_id=reservations[1].id,
                               driving_distance=200,
                               first_section_fee=20,
                               second_section_fee=200,
                               third_section_fee=2000,
                               total_fee=2220)
        payments = [payment_1, payment_2]

        response = self.client.get(f'/reservations/history')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for entry, response_entry in zip(payments, response.data['results']):
            self.assertEqual(entry.reservation.id, response_entry['id'])
            self.assertEqual(entry.member.id, response_entry['member'])
            self.assertEqual(entry.driving_distance, response_entry['distance'])

        for response_entry in response.data['results']:
            self.assertEqual(expected_status, response_entry['reservation_status'])
            self.assertEqual(self.zones[0].id, response_entry['zone'])
            self.assertEqual(self.cars[0].id, response_entry['car'])

    def test_should_list_MemberSelf_with_total_driving_distance(self):
        reservations = baker.make('reservations.Reservation',
                                  member=self.user,
                                  car_id=self.cars[0].id,
                                  zone_id=self.zones[0].id,
                                  _quantity=2)
        payment_1 = baker.make('payments.PaymentAfterUse',
                               member=self.user,
                               reservation_id=reservations[0].id,
                               driving_distance=100,
                               first_section_fee=10,
                               second_section_fee=100,
                               third_section_fee=1000,
                               total_fee=1110)
        payment_2 = baker.make('payments.PaymentAfterUse',
                               member=self.user,
                               reservation_id=reservations[1].id,
                               driving_distance=200,
                               first_section_fee=20,
                               second_section_fee=200,
                               third_section_fee=2000,
                               total_fee=2220)
        response = self.client.get(f'/members')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.user.name, response.data['results'][0]['name'])
        self.assertEqual(self.user.email, response.data['results'][0]['email'])
        self.assertEqual(self.user.phone, response.data['results'][0]['phone'])
        self.assertEqual(payment_1.driving_distance + payment_2.driving_distance,
                         response.data['results'][0]['total_driving_distance'])

    def test_should_create_multi_photos(self):
        """
        Request : POST - /reservations/123/photos
        """
        expected_count = 2
        test_image_1 = ImageMaker.temporary_image(name='test1.jpg')
        test_image_2 = ImageMaker.temporary_image(name='test2.jpg')

        data = {'photos': [test_image_1, test_image_2]}

        response = self.client.post(f'/reservations/{self.reservation.id}/photos', data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response)
        self.assertEqual(PhotoBeforeUse.objects.all().count(), expected_count)

    def test_should_list_photos(self):
        """
        Request : GET - /reservations/123/photos
        """
        expected_count = 2
        entrys = baker.make('reservations.PhotoBeforeUse', image=self.test_image, _quantity=2)

        response = self.client.post(f'/reservations/{self.reservation.id}/photos')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response)

    def test_should_retrieve_Cars_detail_info(self):
        """
        Request : GET - /carzones/123/cars/456/info
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}/info')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(self.cars[0].id, response.data['id'])
        self.assertEqual(self.cars[0].name, response.data['name'])
        self.assertEqual(self.cars[0].zone.id, response.data['zone'])
        self.assertTrue(response.data['image'].endswith(self.cars[0].image.url))
        self.assertEqual(self.cars[0].manufacturer, response.data['manufacturer'])
        self.assertEqual(self.cars[0].fuel_type, response.data['fuel_type'])
        self.assertEqual(self.cars[0].type_of_vehicle, response.data['type_of_vehicle'])
        self.assertEqual(self.cars[0].shift_type, response.data['shift_type'])
        self.assertEqual(self.cars[0].riding_capacity, response.data['riding_capacity'])
        self.assertEqual(self.cars[0].is_event_model, response.data['is_event_model'])
        self.assertEqual(self.cars[0].manual_page, response.data['manual_page'])
        self.assertEqual(self.cars[0].safety_option, response.data['safety_option'])
        self.assertEqual(self.cars[0].convenience_option, response.data['convenience_option'])
        self.assertEqual(self.car_price_1.id, response.data['car_prices']['id'])
        self.assertEqual(self.car_price_1.car_id, response.data['car_prices']['car'])
        self.assertEqual(self.car_price_1.standard_price, response.data['car_prices']['standard_price'])
        self.assertEqual(self.car_price_1.min_price_per_km, response.data['car_prices']['min_price_per_km'])
        self.assertEqual(self.car_price_1.mid_price_per_km, response.data['car_prices']['mid_price_per_km'])
        self.assertEqual(self.car_price_1.max_price_per_km, response.data['car_prices']['max_price_per_km'])

    def test_should_list_coupon(self):
        """
            Request : GET - /members/123/coupons
        """
        coupons = baker.make('prices.Coupon', member_id=self.user.id, title='1일 10000원 쿠폰', discount_fee=10000,
                             expire_date_time=self.coupon_expire_date_time, _quantity=2)

        response = self.client.get(f'/members/{self.user.id}/coupons')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        for entry, response_entry in zip(coupons, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.member.id, response_entry['member'])
            self.assertEqual(entry.title, response_entry['title'])
            self.assertEqual(entry.limit_delta_term, response_entry['limit_delta_term'])
            self.assertEqual(entry.discount_fee, response_entry['discount_fee'])
            self.assertEqual(entry.is_enabled, response_entry['is_enabled'])
            self.assertEqual(entry.is_used, response_entry['is_used'])
            self.assertEqual(entry.will_use_check, response_entry['will_use_check'])
            self.assertEqual(entry.is_free, response_entry['is_free'])

    def test_should_retrive_coupon(self):
        """
            Request : GET - /members/123/coupons/456
        """
        coupons = baker.make('prices.Coupon', member_id=self.user.id, title='1일 10000원 쿠폰', discount_fee=10000,
                             expire_date_time=self.coupon_expire_date_time, _quantity=2)
        response = self.client.get(f'/members/{self.user.id}/coupons/{coupons[0].id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(coupons[0].id, response.data['id'])
        self.assertEqual(coupons[0].member.id, response.data['member'])
        self.assertEqual(coupons[0].title, response.data['title'])
        self.assertEqual(coupons[0].limit_delta_term, response.data['limit_delta_term'])
        self.assertEqual(coupons[0].discount_fee, response.data['discount_fee'])
        self.assertEqual(coupons[0].is_enabled, response.data['is_enabled'])
        self.assertEqual(coupons[0].is_used, response.data['is_used'])
        self.assertEqual(coupons[0].will_use_check, response.data['will_use_check'])
        self.assertEqual(coupons[0].is_free, response.data['is_free'])

    def test_should_use_coupon(self):
        """
            Request : POST - /members/123/coupons/456/use
        """
        coupon = baker.make('prices.Coupon', member_id=self.user.id, title='1일 10000원 쿠폰', discount_fee=10000,
                            expire_date_time=self.coupon_expire_date_time)
        expected_value = True
        response = self.client.get(f'/members/{self.user.id}/coupons/{coupon.id}/use')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(expected_value, response.data['will_use_check'])

    def test_should_discount_coupon_when_use_coupon(self):
        """
                Request : POST - /carzones/123/cars/456/reservations
        """

        coupon = baker.make('prices.Coupon', member_id=self.user.id, title='1일 10000원 쿠폰', discount_fee=10000,
                            expire_date_time=self.coupon_expire_date_time, will_use_check=True)
        expected_status = ReservationStatus.ChoiceStatus.PAID_1.value
        # Credit 초기화
        default_credit = 100000
        self.user.profile.credit_point = default_credit
        self.user.profile.save()

        # 미래 시간으로 data 테스트
        data = {'date_time_start': '2020-10-19T13:10:00Z',
                'date_time_end': '2020-10-19T13:50:00Z',
                'insurance': 'light'}

        response = self.client.post(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}/reservations', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(str(self.zones[0].id), response.data['zone'])
        self.assertEqual(str(self.cars[0].id), response.data['car'])
        self.assertEqual(data['insurance'], response.data['insurance'])
        self.assertEqual(data['date_time_start'], response.data['date_time_start'])
        self.assertEqual(data['date_time_end'], response.data['date_time_end'])
        # Status Check
        self.assertTrue(ReservationStatus.objects.filter(reservation_id=response.data['id']).exists())
        self.assertEqual(expected_status,
                         ReservationStatus.objects.get(reservation_id=response.data['id']).status)
        # Payment Check
        self.assertTrue(PaymentBeforeUse.objects.filter(reservation_id=response.data['id']).exists())
        rental_fee = self.car_price_1.standard_price + self.car_price_1.weekday_price_per_ten_min
        insurance_fee = self.insurance_1.light_price + self.insurance_1.light_price_per_ten_min
        self.assertEqual(rental_fee, PaymentBeforeUse.objects.get(reservation_id=response.data['id']).rental_fee)
        self.assertEqual(insurance_fee, PaymentBeforeUse.objects.get(reservation_id=response.data['id']).insurance_fee)
        self.assertEqual(rental_fee + insurance_fee - coupon.discount_fee,
                         PaymentBeforeUse.objects.get(reservation_id=response.data['id']).total_fee)

        # Credit Check
        self.assertEqual(default_credit - rental_fee - insurance_fee + coupon.discount_fee,
                         Profile.objects.get(member_id=self.user.id).credit_point)
