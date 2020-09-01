from members.models import Member, Profile
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class MembersSerializer(ModelSerializer):
    """
    회원가입 Serializer
    """

    class Meta:
        model = Member
        fields = (
            'id',
            'email',
            'password',
            'registration_id',
        )

        extra_kwargs = {
            'password': {'write_only': True},
            'registration_id': {'write_only': True}
        }

    def validate_registration_id(self, attr):
        if len(attr) == 7:
            return attr
        raise serializers.ValidationError('주민등록번호가 일치하지 않습니다.')


class ChangePasswordSerializer(ModelSerializer):
    """
    비밀번호 변경 Serializer
    """
    change_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Member
        fields = (
            'password',
            'change_password',
        )

    def validate_password(self, attr):
        member = self.instance

        if member.check_password(attr):
            return attr

        raise serializers.ValidationError('비밀번호가 일치하지 않습니다.')


class ProfileSerializer(ModelSerializer):
    """
    프로필 Serializer
    """

    class Meta:
        model = Profile
        fields = (
            'id',
            'image',
            'birth',
        )
