from django.urls import path
from .views import csrf, register

urlpatterns = [
    path('auth/csrf/', csrf, name='auth-csrf'),
    path('auth/register/', register, name='auth-register'),
]
