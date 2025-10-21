from users.views import *
from django.urls import path

urlpatterns = [
    path('register', register_user, name='register_user'),
    path('login', login_user, name='login_user'),
    path('token/refresh', refresh_token, name='refresh_token'),
]
