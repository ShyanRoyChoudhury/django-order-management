from rest_framework import serializers
from orders.models import Order

class CreateOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=Order.Status.choices, read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['product_name', 'quantity', 'status', 'amount']