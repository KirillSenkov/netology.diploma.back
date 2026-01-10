from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    storage_rel_path = models.CharField(
        max_length=255,
        unique=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        if not self.storage_rel_path:
            self.storage_rel_path = f'{self.username}__{uuid.uuid4()}/'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
