from datetime import date

from members.models import Member, Profile, PhoneAuth
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
            'name',
            'email',
            'password',
        )

        extra_kwargs = {
            'password': {'write_only': True},
        }


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
    name = serializers.CharField(source='member.name')

    class Meta:
        model = Profile
        fields = (
            'id',
            'image',
            'name',
            'credit_point',
        )


class PhoneAuthSerializer(ModelSerializer):
    class Meta:
        model = PhoneAuth
        fields = (
            'id',
            'auth_number',
            'phone_number',
            'registration_id',
        )

        read_only_fields = ('auth_number',)

    def validate_registration_id(self, attrs):
        if not len(attrs) == 7:
            raise serializers.ValidationError('생년월일을 입력해주세요.')

        if attrs[-1:] in ['1', '2']:
            birth = date(int(f'19{attrs[0:2]}'), int(attrs[2:4]), int(attrs[4:6]))
            year = (date.today() - birth).days / 365

            if year >= 23:
                return attrs
            else:
                raise serializers.ValidationError('23세 이하는 가입할수 없습니다.')

        elif attrs[-1:] in ['3', '4']:
            birth = date(int(f'20{attrs[0:2]}'), int(attrs[2:4]), int(attrs[4:6]))
            year = (date.today() - birth).days / 365

            if year >= 23:
                return attrs
            else:
                raise serializers.ValidationError('23세 이하는 가입할수 없습니다.')


class CheckAuthNumberSerializer(ModelSerializer):
    check_auth_number = serializers.IntegerField(write_only=True)

    class Meta:
        model = PhoneAuth
        fields = (
            'id',
            'check_auth_number',
        )

        read_only_fields = ('auth_number',)

    def validate_check_auth_number(self, attrs):
        if len(str(attrs)) == 6:
            return attrs
        else:
            raise serializers.ValidationError('6자리를 입력해주세요.')
