from django.db import models
from bookmarks.models import Bookmark
from django.core.files import File
from django.conf import settings
from django.dispatch import receiver
import os
import uuid

from django_q.tasks import async_task

class SinglePageArchive(models.Model):
    bookmark = models.ForeignKey(
        "bookmarks.Bookmark", on_delete=models.CASCADE, related_name="page_archives"
    )
    date_taken = models.DateTimeField(auto_now_add=True)
    rel_file_path = models.CharField(max_length=500)
    uuid = models.UUIDField(default=uuid.uuid4)


class MediaArchive(models.Model):
    bookmark = models.ForeignKey(
        "bookmarks.Bookmark", on_delete=models.CASCADE, related_name="media_archives"
    )
    date_taken = models.DateTimeField(auto_now_add=True)
    rel_file_path = models.CharField(max_length=500)
    uuid = models.UUIDField(default=uuid.uuid4)


class VideoArchive(models.Model):
    bookmark = models.ForeignKey(
        "bookmarks.Bookmark", on_delete=models.CASCADE, related_name="video_archives"
    )
    date_taken = models.DateTimeField(auto_now_add=True)
    rel_file_path = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    uuid = models.UUIDField(default=uuid.uuid4)


@receiver(models.signals.post_delete, sender=SinglePageArchive)
def single_page_archive_delete_file(sender, instance, **kwargs):
    if instance.rel_file_path:
        file_path = os.path.join(settings.MEDIA_ROOT, instance.rel_file_path)
        if os.path.isfile(file_path):
            async_task(os.remove, file_path)
            
    rm_empty_bookmark_dir(str(instance.bookmark.uuid))

# @receiver(models.signals.post_delete, sender=MediaArchive)
# def media_archive_delete_file(sender, instance, **kwargs):
#     if instance.media_file_path:
#         if os.path.isfile(instance.media_file_path):
#             os.remove(instance.media_file_path)

@receiver(models.signals.post_delete, sender=VideoArchive)
def video_page_archive_delete_file(sender, instance, **kwargs):
    if instance.rel_file_path:
        file_path = os.path.join(settings.MEDIA_ROOT, instance.rel_file_path)
        if os.path.isfile(file_path):
            async_task(os.remove, file_path)

    rm_empty_bookmark_dir(str(instance.bookmark.uuid))

def rm_empty_bookmark_dir(bookmark_uuid):
    dir_path = os.path.join(settings.MEDIA_ROOT, bookmark_uuid)
    if not os.path.exists(dir_path):
        return
    
    files = os.listdir(dir_path)
    if len(files) == 0:
        async_task(os.rmdir, dir_path)
