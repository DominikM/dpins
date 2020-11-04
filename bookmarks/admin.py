from django.contrib import admin

from .models import Bookmark, Tag
# Register your models here.

admin.site.register(Bookmark)
admin.site.register(Tag)
