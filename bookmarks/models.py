from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Bookmark(models.Model):
    title = models.CharField(max_length=300)
    tags = models.ManyToManyField('Tag', related_name="bookmarks", blank=True)
    url = models.URLField()
    date_time_added = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    
    def __str__(self):
        return f"\"{self.title}\" from {self.user}"


class Tag(models.Model):
    word = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"\"{self.word}\""
