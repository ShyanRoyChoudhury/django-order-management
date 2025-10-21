from users.views import *
from django.urls import path
from orders.views import *

# urlpatterns = [
#     path('', create_order, name='create_order'),
#     path('', get_order, name='get_orders'),
#     # 
# ]


urlpatterns = [
    path('', orders_handler, name='orders_handler'),  # Handles both GET and POST at /orders/
    path('<str:order_id>/cancel', cancel_orders_handler, name='cancel_order')
]