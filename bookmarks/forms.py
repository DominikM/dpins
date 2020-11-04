from django.forms import Form, URLField, CharField, BooleanField, HiddenInput

from .models import Bookmark

class BookmarkForm(Form):
    title = CharField(label='Title', max_length=300)
    url = URLField(label='URL')
    tags = CharField(label='tags', required=False)
    auto_close = BooleanField(initial=False, widget=HiddenInput(), required=False)


class SimpleSearchForm(Form):
    query = CharField(label='Search')
