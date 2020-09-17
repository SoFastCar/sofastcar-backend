from django.test import TestCase

# Create your tests here.
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from cars.tests import ImageMaker
from members.models import Member


class CarPriceTestCase(APITestCase):
    def setUp(self):
        self.user = Member.objects.create(email='test@example.com',
                                          password='test')
        self.test_image = ImageMaker.temporary_image()
        self.zones = baker.make('carzones.CarZone', _quantity=2)
        self.cars = baker.make('cars.Car', zone=self.zones[0],
                               image=self.test_image.name, _quantity=2)
        self.client.force_authenticate(user=self.user)

    def test_should_list_CarPrices(self):
        """
        Request : GET - /carzones/123/cars/456/prices
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}/prices')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for entry, response_entry in zip(self.cars, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.car, response_entry['car'])
            self.assertEqual(entry.standard_price, response_entry['standard_price'])
            self.assertEqual(entry.min_price_per_km, response_entry['min_price_per_km'])
            self.assertEqual(entry.mid_price_per_km, response_entry['mid_price_per_km'])
            self.assertEqual(entry.max_price_per_km, response_entry['max_price_per_km'])