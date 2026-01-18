from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_fix_storage_rel_path'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(
                name='users_user_storage_rel_path_not_empty',
                check=~Q(storage_rel_path=''),
            ),
        ),
    ]
