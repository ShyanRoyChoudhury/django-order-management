from users.views import *
from django.urls import path

urlpatterns = [
    path('orders', register_user, name='register_user'),
    path('orders', login_user, name='login_user'),
    path('orders/<int:order_id>/cancel', cancel_order, name='cancel_order')
]
