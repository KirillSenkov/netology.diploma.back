from django.urls import path
from .views import upload_file, list_files, delete_file, rename_file

urlpatterns = [
    path('files/upload/', upload_file, name='files-upload'),
    path('files/', list_files, name='files-list'),
    path('files/<int:file_id>/', delete_file, name='files-delete'),
    path('files/<int:file_id>/rename/', rename_file, name='files-rename'),
]