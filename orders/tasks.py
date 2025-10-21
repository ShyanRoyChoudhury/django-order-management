import logging
from celery import shared_task
from .models import Order, Status
import time

logger = logging.getLogger(__name__)


@shared_task
def process_pending_orders():
    print("Starting to process pending orders...")
    pending_orders = Order.objects.filter(status=Status.PENDING)
    if not pending_orders.exists():
        logger.info('No pending orders found.')
        return


    ids = list(pending_orders.values_list('id', flat=True))
    logger.info('Processing orders: %s', ids)
    pending_orders.update(status=Status.PROCESSING)


    # Simulate processing
    time.sleep(10)


    Order.objects.filter(id__in=ids).update(status=Status.COMPLETED)
    logger.info('Completed orders: %s', ids)