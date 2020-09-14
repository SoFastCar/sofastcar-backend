from django.test import TestCase

# Create your tests here.
from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from carzones.models import CarZone
from members.models import Member


class CarZoneTestCase(APITestCase):
    def setUp(self):
        self.user = Member.objects.create(email='test@example.com',
                                          password='test')
        self.zones = baker.make('carzones.CarZone', _quantity=2)
        self.expected_count = 2
        self.client.force_authenticate(user=self.user)

    def test_should_list_CarZones(self):
        """
        Request : GET - /carzones
        """
        response = self.client.get('/carzones')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry, response_entry in zip(self.zones, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.name, response_entry['name'])
            self.assertEqual(entry.latitude, response_entry['latitude'])
            self.assertEqual(entry.longitude, response_entry['longitude'])
            self.assertEqual(entry.type, response_entry['type'])
            self.assertEqual(entry.address, response_entry['address'])
            self.assertEqual(entry.sub_info, response_entry['sub_info'])

    def test_should_retrieve_CarZone(self):
        """
        Request : GET - /carzones/{id}
        """
        response = self.client.get(f'/carzones/{self.zones[0].id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.zones[0].id, response.data['id'])
        self.assertEqual(self.zones[0].name, response.data['name'])
        self.assertEqual(self.zones[0].latitude, response.data['latitude'])
        self.assertEqual(self.zones[0].longitude, response.data['longitude'])
        self.assertEqual(self.zones[0].type, response.data['type'])
        self.assertEqual(self.zones[0].address, response.data['address'])
        self.assertEqual(self.zones[0].sub_info, response.data['sub_info'])

    def test_should_list_CarZones_from_search_address(self):
        """
        Request : GET - /carzones?keyword=foo
        """
        CarZone.objects.create(name='zone1', address='서울 광진구 자양동')
        CarZone.objects.create(name='zone2', address='서울 성동구 성수동1가')
        CarZone.objects.create(name='zone3', address='서울 성동구 성수동2가')
        response = self.client.get('/carzones?keyword=성수동')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CarZone.objects.filter(address__icontains='성수동').count(), self.expected_count)

    def test_should_list_CarZones_from_search_name(self):
        """
        Request : GET - /carzones?keyword=name
        """
        CarZone.objects.create(name='zone1', address='서울 광진구 자양동')
        CarZone.objects.create(name='zone2', address='서울 성동구 성수동1가')
        CarZone.objects.create(name='nothing', address='서울 성동구 성수동2가')
        response = self.client.get('/carzones?keyword=zone')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CarZone.objects.filter(name__icontains='zone').count(), self.expected_count)

    def test_should_list_CarZones_filter_by_distance(self):
        """
        Request : GET - /carzones/distance?lat=123.456&lon=123.456&distance=1
        """
        CarZone.objects.create(name='zone1', address='서울 송파구 장지동',
                               latitude=37.469361, longitude=127.1259747)
        CarZone.objects.create(name='zone2', address='서울 성동구 성수동1가',
                               latitude=37.540323, longitude=127.042847)
        CarZone.objects.create(name='zone3', address='서울 성동구 성수동1가',
                               latitude=37.5418042, longitude=127.0436044)
        response = self.client.get(f'/carzones/distance?lat=37.54&lon=127.04&distance=1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.data:
            self.assertEqual(entry['address'], '서울 성동구 성수동1가')