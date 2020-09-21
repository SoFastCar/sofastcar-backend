from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.serializers import PaymentCreateSerializer


class PaymentCreateViews(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(reservation__member=self.request.user)
