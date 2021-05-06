from django.contrib import admin

from .models import SinglePageArchive, VideoArchive

# Register your models here.

admin.site.register(SinglePageArchive)
admin.site.register(VideoArchive)
