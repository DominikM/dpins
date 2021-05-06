from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from bookmarks.models import Bookmark

import os


@login_required
def show_archive(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("bm"))

    payload = {'bookmark': bookmark}

    single_pages = bookmark.page_archives.all()
    if single_pages:
        payload['archived_page_url'] = os.path.join(
            settings.MEDIA_URL, single_pages[0].rel_file_path
        )

    videos = bookmark.video_archives.order_by('date_taken')
    if videos:
        payload['videos'] = []
        for video in videos:
            video_dict = {}
            video_dict['title'] = video.title
            video_dict['url'] = os.path.join(
                settings.MEDIA_URL, videos[0].rel_file_path
            )
            payload['videos'].append(video_dict)

    print(payload)
    return render(
        request,
        "archiver.html",
        payload,
    )
