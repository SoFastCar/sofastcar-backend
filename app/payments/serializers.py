from rest_framework.serializers import ModelSerializer

from payments.models import PaymentBeforeUse


class PaymentBeforeUseSerializer(ModelSerializer):
    class Meta:
        model = PaymentBeforeUse
        fields = ['id',
                  'member',
                  'reservation',
                  'rental_fee',
                  'insurance_fee',
                  'coupon_discount',
                  'etc_discount',
                  'extension_fee',
                  'total_fee',
                  'created_at',
                  'updated_at']
        read_only_fields = ['id',
                            'member',
                            'reservation',
                            'rental_fee',
                            'insurance_fee',
                            'coupon_discount',
                            'etc_discount',
                            'extension_fee',
                            'total_fee',
                            'created_at',
                            'updated_at']
