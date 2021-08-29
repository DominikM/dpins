from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Bookmark(models.Model):
    title = models.TextField()
    tags = models.ManyToManyField('Tag', related_name="bookmarks", blank=True)
    to_read = models.BooleanField(default=False)
    url = models.URLField(max_length=500)
    date_time_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    
    def __str__(self):
        return f"\"{self.title}\" from {self.user}"


class Tag(models.Model):
    word = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"\"{self.word}\""
