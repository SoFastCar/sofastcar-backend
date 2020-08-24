from rest_framework import status
from rest_framework.test import APITestCase

from members.models import Member


class MemberTestCase(APITestCase):
    def setUp(self):
        self.member = Member.objects.create(
            email='member@member.com',
            password='member'
        )

    def test_create_member(self):
        data = {
            'email': 'test@test.com',
            'password': 'test',
            'confirm_password': 'test'
        }
        response = self.client.post('/members/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])

    def test_delete_member(self):
        response = self.client.delete(f'/members/{self.member.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Member.objects.filter(id=self.member.id))

    def test_change_password(self):
        data = {
            'password': 'member',
            'change_password': 'test',
            'confirm_password': 'test'
        }
        self.client.force_authenticate(user=self.member)
        response = self.client.put(f'/members/{self.member.id}/change_password/', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
