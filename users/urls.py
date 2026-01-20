from django.urls import path
from .views import (
    csrf,
    register,
    login_view,
    admin_users_list,
    admin_user_delete,
    # admin_user_set_level
)

urlpatterns = [
    path('auth/csrf/', csrf, name='auth-csrf'),
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', login_view, name='auth-login'),
    path('admin/users/', admin_users_list, name='admin-users'),
    path('admin/users/<int:user_id>/', admin_user_delete,
         name='admin-user-delete'),
    #path('admin/users/<int:user_id>/level/', admin_user_set_level,
         #name='admin-user-set-level'),
]
