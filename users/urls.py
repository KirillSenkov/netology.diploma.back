from django.urls import path
from .views import csrf

urlpatterns = [
    path('auth/csrf/', csrf, name='auth-csrf'),
]
