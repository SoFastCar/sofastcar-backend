import datetime
import io

from PIL import Image
from django.test import TestCase

# Create your tests here.
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

# from cars.models import PhotoBeforeUse
from cars.models import CarTimeTable
from core.utils import trans_kst_to_utc
from members.models import Member
from prices.models import InsuranceFee


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
                                          password='test')
        self.test_image = ImageMaker.temporary_image()
        self.zones = baker.make('carzones.CarZone', _quantity=2)
        self.cars = baker.make('cars.Car', zone=self.zones[0],
                               image=self.test_image.name, _quantity=2)
        # 테스트용 차량 가격 2개
        self.car_price_1 = baker.make('prices.CarPrice', car=self.cars[0], standard_price=1000,
                                      weekday_price_per_ten_min=10)
        self.car_price_2 = baker.make('prices.CarPrice', car=self.cars[1], standard_price=2000,
                                      weekday_price_per_ten_min=20)
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
        # self.reservations = baker.make('reservations.Reservation', member=self.user, _quantity=2)
        self.client.force_authenticate(user=self.user)

    def test_should_list_Cars_and_CarPrices(self):
        """
        Request : GET - /carzones/123/cars
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars')

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
        Request : GET - /carzones/123/cars/456
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

    # def test_should_create_multi_photos(self):
    #     """
    #     Request : POST - /reservations/123/photos
    #     """
    #     expected_count = 2
    #     test_image_1 = ImageMaker.temporary_image(name='test1.jpg')
    #     test_image_2 = ImageMaker.temporary_image(name='test2.jpg')
    #
    #     data = {'photos': [test_image_1, test_image_2]}
    #
    #     response = self.client.post(f'/reservations/{self.reservations[0].id}/photos', data=data, format='multipart')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED, response)
    #     self.assertEqual(PhotoBeforeUse.objects.all().count(), expected_count)
