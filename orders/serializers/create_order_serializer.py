from rest_framework import serializers
from orders.models import Order, Status

class CreateOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['product_name', 'quantity', 'amount']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['status'] = Status.PENDING
        order = Order.objects.create(user=user, **validated_data)
        return order