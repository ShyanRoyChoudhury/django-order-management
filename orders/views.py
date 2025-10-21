from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    try:
        # Logic to create an order
        order_data = request.data
        # Assume OrderSerializer exists and is imported
        serializer = OrderSerializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({'order_id': order.id, 'message': "Order created"}, status=201)

    except Exception as e:
        logger.error("Error creating order: %s", str(e))
        return Response({'error': str(e)}, status=400)