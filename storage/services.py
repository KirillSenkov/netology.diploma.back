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
