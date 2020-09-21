from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.exceptions import PaymentDoesNotExistException
from payment.models import Payment
from payment.serializers import PaymentCreateSerializer, PaymentRentalHistorySerializer


class PaymentCreateViews(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(reservation__member=self.request.user)


class PaymentRentalHistoryViews(generics.RetrieveAPIView):
    serializer_class = PaymentRentalHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            reservation = Payment.objects.get(pk=self.kwargs['payment_id'])
            return reservation
        except ObjectDoesNotExist:
            raise PaymentDoesNotExistException
