from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer
from . import notifications


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # ensure serializer has request context and will use CurrentUserDefault
        order = serializer.save()

        notifications.send_order_email(order)

        notifications.send_order_sms(order)
