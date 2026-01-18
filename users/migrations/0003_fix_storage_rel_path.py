from pathlib import Path
import uuid

from django.conf import settings
from django.db import migrations


def fix_storage_rel_path(apps, schema_editor):
    User = apps.get_model('users', 'User')

    storage_root = Path(settings.STORAGE_ROOT)
    storage_root.mkdir(parents=True, exist_ok=True)

    bad_users = User.objects.filter(storage_rel_path='') | User.objects.filter(storage_rel_path__regex=r'^\s+$')

    for u in bad_users:
        new_path = f'{u.username}_{uuid.uuid4()}/'
        u.storage_rel_path = new_path
        u.save(update_fields=['storage_rel_path'])

        user_dir = storage_root / new_path
        user_dir.mkdir(parents=True, exist_ok=True)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_admin'),
    ]

    operations = [
        migrations.RunPython(fix_storage_rel_path, migrations.RunPython.noop),
    ]
