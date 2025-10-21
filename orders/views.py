from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from orders.serializers.create_order_serializer import CreateOrderSerializer
from orders.serializers.list_order_serializer import OrderSerializer
from orders.serializers.cancel_order_serializer import CancelOrderSerializer
from orders.tasks import add
import logging


logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_handler(request):
    try:
        if request.method == 'POST':
            serializer = CreateOrderSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            return Response({'order_id': order.uid, 'message': "Order created"}, status=201)

        elif request.method == 'GET':
            orders = request.user.orders.all()
            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginated_orders = paginator.paginate_queryset(orders, request)
            serializer = OrderSerializer(paginated_orders, many=True)
            add.delay(10,20)
            return paginator.get_paginated_response(serializer.data)

    except serializers.ValidationError as e:
        errors = {field: [str(detail) for detail in details] for field, details in e.detail.items()}
        return Response({'errors': errors}, status=409)
    except Exception as e:
        logger.error("Unexpected error during order handling: %s", str(e))
        errors = {'non_field_errors': [str(e)]}
        return Response({'errors': errors, 'message': 'Something went wrong'}, status=500)
    


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_orders_handler(request, order_id):
    try:
        serializer = CancelOrderSerializer(data={'order_id': order_id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({'order_id': order.uid, 'message': "Order cancelled"}, status=200)

    except serializers.ValidationError as e:
        detail = e.detail

        # handle both list and dict cases
        if isinstance(detail, list):
            if any("Order not found" in str(d) for d in detail):
                return Response({'errors': detail}, status=404)
        elif isinstance(detail, dict):
            if any("Order not found" in str(d) for v in detail.values() for d in (v if isinstance(v, list) else [v])):
                return Response({'errors': detail}, status=404)
    
    except Exception as e:
        logger.error("Unexpected error during order cancelation: %s", str(e))
        errors = {'non_field_errors': [str(e)]}
        return Response({'errors': errors, 'message': 'Something went wrong'}, status=500)