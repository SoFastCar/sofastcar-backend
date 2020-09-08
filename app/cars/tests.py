from django.test import TestCase

# Create your tests here.
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from cars.models import ImageMaker
from members.models import Member


class CarTestCase(APITestCase):
    def setUp(self):
        self.user = Member.objects.create(email='test@example.com',
                                          password='test')
        self.test_image = ImageMaker.temporary_image()
        self.zones = baker.make('carzones.CarZone', _quantity=2)
        self.cars = baker.make('cars.Car', zone=self.zones[0],
                               image=self.test_image.name, _quantity=2)
        self.client.force_authenticate(user=self.user)

    def test_should_list_Cars(self):
        """
        Request : GET - /carzones/123/cars
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for entry, response_entry in zip(self.cars, response.data):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.name, response_entry['name'])
            self.assertEqual(entry.zone.id, response_entry['zone'])
            self.assertTrue('.jpg' in response_entry['image'])
            self.assertEqual(entry.manufacturer, response_entry['manufacturer'])
            self.assertEqual(entry.fuel, response_entry['fuel'])
            self.assertEqual(entry.type, response_entry['type'])
            self.assertEqual(entry.shift_type, response_entry['shift_type'])
            self.assertEqual(entry.riding_capacity, response_entry['riding_capacity'])
            self.assertEqual(entry.is_event_model, response_entry['is_event_model'])
            self.assertEqual(entry.manual_page, response_entry['manual_page'])
            self.assertEqual(entry.safety_option, response_entry['safety_option'])
            self.assertEqual(entry.convenience_option, response_entry['convenience_option'])

    def test_should_retrieve_Cars(self):
        """
        Request : GET - /carzones/123/cars/456
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}/cars/{self.cars[0].id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.cars[0].id, response.data['id'])
        self.assertEqual(self.cars[0].name, response.data['name'])
        self.assertEqual(self.cars[0].zone.id, response.data['zone'])
        self.assertTrue('.jpg' in response.data['image'])
        self.assertEqual(self.cars[0].manufacturer, response.data['manufacturer'])
        self.assertEqual(self.cars[0].fuel, response.data['fuel'])
        self.assertEqual(self.cars[0].type, response.data['type'])
        self.assertEqual(self.cars[0].shift_type, response.data['shift_type'])
        self.assertEqual(self.cars[0].riding_capacity, response.data['riding_capacity'])
        self.assertEqual(self.cars[0].is_event_model, response.data['is_event_model'])
        self.assertEqual(self.cars[0].manual_page, response.data['manual_page'])
        self.assertEqual(self.cars[0].safety_option, response.data['safety_option'])
        self.assertEqual(self.cars[0].convenience_option, response.data['convenience_option'])