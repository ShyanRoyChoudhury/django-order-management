from rest_framework import serializers
from orders.models import Order, Status

class CancelOrderSerializer(serializers.ModelSerializer):

    order_id = serializers.CharField(max_length=255)
    class Meta:
        model = Order
        fields = ['order_id']

    def create(self, validated_data):
        order_id = validated_data.get('order_id')
        try:
            order = Order.objects.get(uid=order_id)
            order.status = Status.CANCELLED
            order.save()
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")