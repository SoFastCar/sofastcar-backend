from members.models import Member
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class MembersSerializer(ModelSerializer):
    """
    회원가입 Serializer
    """
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Member
        fields = (
            'id',
            'email',
            'password',
            'confirm_password',
        )

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, attrs):
        confirm_password = attrs.pop('confirm_password')
        if confirm_password != attrs.get('password'):
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')

        return attrs


class ChangePasswordSerializer(ModelSerializer):
    """
    비밀번호 변경 Serializer
    """
    change_password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Member
        fields = (
            'password',
            'change_password',
            'confirm_password',
        )

    def validate(self, attrs):
        if attrs['change_password'] == attrs['confirm_password']:
            return attrs['change_password']
        else:
            raise serializers.ValidationError('비밀번호가 서로 다릅니다.')

    def validate_password(self, attr):
        member = self.instance

        if member.check_password(attr):
            return attr

        raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')
