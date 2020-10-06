from django.test import TestCase

# Create your tests here.
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from cars.tests import ImageMaker
from members.models import Member


class EventPhotoTestCase(APITestCase):
    def setUp(self):
        self.user = Member.objects.create(email='test@example.com',
                                          password='test')
        self.expected_count = 2
        self.test_image = ImageMaker.temporary_image()
        self.event_photos = baker.make('events.EventPhoto', image=self.test_image.name, _quantity=2)
        self.client.force_authenticate(user=self.user)

    def test_should_list_EventPhotos(self):
        """
        Request : GET - /event_photos
        """
        response = self.client.get('/event_photos')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for entry, response_entry in zip(self.event_photos, response.data['results']):
            self.assertEqual(entry.id, response_entry['id'])
            self.assertEqual(entry.name, response_entry['name'])
            self.assertTrue('.jpg' in response_entry['image'])

    def test_should_retrieve_EventPhoto(self):
        """
        Request : GET - /event_photos/123
        """
        response = self.client.get(f'/event_photos/{self.event_photos[0].id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.event_photos[0].id, response.data['id'])
        self.assertEqual(self.event_photos[0].name, response.data['name'])
        self.assertTrue('.jpg' in response.data['image'])
