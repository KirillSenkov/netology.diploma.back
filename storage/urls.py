from django.urls import path
from .views import (
    upload_file,
    list_files,
    delete_file,
    rename_file,
    download_file,
    comment_file,
    enable_share,
    disable_share,
    download_shared,
)

urlpatterns = [
    path('files/upload/', upload_file, name='files-upload'),
    path('files/', list_files, name='files-list'),
    path('files/<int:file_id>/', delete_file, name='files-delete'),
    path('files/<int:file_id>/rename/', rename_file, name='files-rename'),
    path('files/<int:file_id>/download/', download_file, name='files-download'),
    path('files/<int:file_id>/comment/', comment_file, name='files-comment'),
    path('files/<int:file_id>/share/', enable_share,
         name='files-share-enable'),
    path('files/<int:file_id>/share/disable/', disable_share,
         name='files-share-disable'),
    path('share/<uuid:token>/', download_shared, name='files-share-download'),
]