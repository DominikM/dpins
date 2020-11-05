from django.forms import Form, URLField, CharField, BooleanField, HiddenInput, FileField

from .models import Bookmark

class BookmarkForm(Form):
    title = CharField(label='Title')
    url = URLField(label='URL')
    tags = CharField(label='tags', required=False)
    auto_close = BooleanField(initial=False, widget=HiddenInput(), required=False)


class ImportFileForm(Form):
    html = FileField(label='File')
