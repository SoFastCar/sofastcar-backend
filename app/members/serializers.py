from members.models import Member
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class MembersSerializer(ModelSerializer):
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Member
        fields = (
            'id',
            'email',
            'password',
            'confirm_password'
        )

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, data):
        confirm_password = data.pop('confirm_password')
        if confirm_password != data.get('password'):
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')

        return data
