import uuid
from django.conf import settings
from django.db import models

class File(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files',
    )

    original_name = models.CharField(max_length=255)
    stored_name = models.CharField(max_length=255, unique=True)
    relative_path = models.CharField(max_length=500)

    size_bytes = models.BigIntegerField()

    comment = models.TextField(blank=True, null=True)

    uploaded = models.DateTimeField(auto_now_add=True)
    last_downloaded = models.DateTimeField(blank=True, null=True)

    share_token = models.UUIDField(unique=True, blank=True, null=True)
    share_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.original_name} ({self.owner})'