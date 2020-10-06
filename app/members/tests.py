from rest_framework import status
from rest_framework.test import APITestCase

from members.models import Member


class MemberTestCase(APITestCase):
    def setUp(self):
        self.member = Member.objects.create(
            name='test',
            email='member@member.com',
            password='member',
            phone='01012345678'
        )

    def test_create_member(self):
        data = {
            'name': 'test',
            'email': 'test@test.com',
            'password': 'test',
            'phone': '01012345678'
        }
        response = self.client.post('/members', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['phone'], data['phone'])

    def test_delete_member(self):
        response = self.client.delete(f'/members/{self.member.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Member.objects.filter(id=self.member.id))

    def test_change_password(self):
        data = {
            'password': 'member',
            'change_password': 'test'
        }
        self.client.force_authenticate(user=self.member)
        response = self.client.put(f'/members/{self.member.id}/change_password', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

