import os
import uuid
from pathlib import Path
from django.conf import settings

def make_stored_name(original_name: str) -> str:
    _, ext = os.path.splitext(original_name)
    return f'{uuid.uuid4().hex}{ext.lower()}'

def user_storage_dir(storage_rel_path: str) -> Path:
    return Path(settings.STORAGE_ROOT) / storage_rel_path

def write_file(file_obj, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with target_path.open('wb') as out:
        for chunk in file_obj.chunks():
            out.write(chunk)

def get_file_for_user(request, file_id):
    querry = File.objects.filter(id=file_id)

    if not request.user.is_admin:
        querry = querry.filter(owner=request.user)

    return querry.first()

def ensure_storage_root() -> Path:
    root = Path(settings.STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root

def ensure_user_storage_dir(storage_rel_path: str) -> Path:
    root = ensure_storage_root()
    user_dir = root / storage_rel_path
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir
