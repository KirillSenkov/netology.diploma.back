import os
from uuid import uuid4
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model

from users.services import can_manage_files
from .models import File

User = get_user_model()
def make_stored_name(original_name: str) -> str:
    _, ext = os.path.splitext(original_name)
    return f'{uuid4().hex}{ext.lower()}'

def user_storage_dir(storage_rel_path: str) -> Path:
    return Path(settings.STORAGE_ROOT) / storage_rel_path

def write_file(file_obj, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with target_path.open('wb') as out:
        for chunk in file_obj.chunks():
            out.write(chunk)

def get_file_for_user(request, file_id):
    file_obj = File.objects.select_related('owner')\
        .filter(id=file_id).first()

    if not file_obj:
        return None

    if can_manage_files(request.user, file_obj.owner):
        return file_obj

    return None

def ensure_storage_root() -> Path:
    root = Path(settings.STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root

def ensure_user_storage_dir(storage_rel_path: str) -> Path:
    root = ensure_storage_root()
    user_dir = root / storage_rel_path
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir
