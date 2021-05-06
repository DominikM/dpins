from django import forms

from .models import Bookmark


class BookmarkForm(forms.Form):
    title = forms.CharField(label="Title", required=False)
    url = forms.URLField(label="URL")
    tags = forms.CharField(label="tags", required=False)
    to_read = forms.BooleanField(label="To read", initial=False, required=False)
    auto_close = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(), required=False
    )


class ImportFileForm(forms.Form):
    html = forms.FileField(label="File")
