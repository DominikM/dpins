import subprocess
import os
import uuid
from django.conf import settings
from .models import SinglePageArchive, VideoArchive
import youtube_dl
import re
import pprint

DOWNLOAD_RE = re.compile("^\[download\] Destination: ([\da-zA-Z-\s._\/]+)$")
MERGE_RE = re.compile('^\[ffmpeg\] Merging formats into "([a-zA-Z\s\-\d_\/.]+)"$')
GOOGLEBOT_USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://google.com/bot.html)"
BINGBOT_USER_AGENT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/69.69.69.69 Safari/537.36 Edg/69.69.69.69"


def download_single_page(url, abs_path):
    command = [
        settings.SINGLEFILE_PATH,
        "--output-directory=" + os.path.dirname(abs_path),
        "--filename-template=" + os.path.basename(abs_path),
        "--back-end=webdriver-chromium",
        url,
    ]
    subprocess.run(command)


def maybe_create_bookmark_dir(bookmark_uuid: str):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, bookmark_uuid)):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, bookmark_uuid))


class YoutubeDLManager:
    def __init__(self, bookmark, bookmark_path):
        self.bookmark = bookmark
        self.bookmark_path = bookmark_path
        self.videos = []

    def progress_hook(self, i, info):
        if info["status"] == "finished":
            print(info)
            rel_bookmark_path = os.path.basename(self.bookmark_path)
            base_filename = os.path.basename(info["filename"]).split(".")[0]
            self.videos[i].rel_file_path = os.path.join(
                rel_bookmark_path, base_filename + ".mp4"
            )
            self.videos[i].save()

    def match_filter_init(self, info_dict):
        result = self.match_filter(info_dict)
        if result is not None:
            self.videos.append(None)
            return result

        vid = VideoArchive.objects.create(
            bookmark=self.bookmark, title=info_dict["title"]
        )
        self.videos.append(vid)

    def match_filter(self, info_dict):
        if "is_live" in info_dict and info_dict["is_live"]:
            self.live = True
            return "Live stream, not downloading"

        return None


def download_videos(bookmark, bookmark_path):
    info = YoutubeDLManager(bookmark, bookmark_path)
    opts = {
        "outtmpl": os.path.join(bookmark_path, "%(title).100s.%(ext)s"),
        "match_filter": info.match_filter_init,
        "merge_output_format": "mp4",
        "simulate": True,
        "restrictfilenames": True,
    }
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            ydl.download([bookmark.url])
        except youtube_dl.DownloadError:
            print('Unable to download videos.')
            return

    print(info.videos)
    for i, vid in enumerate(info.videos):
        if vid is None:
            continue
        
        opts = {
            "outtmpl": os.path.join(bookmark_path, "%(title).100s.%(ext)s"),
            "match_filter": info.match_filter,
            "progress_hooks": [lambda status: info.progress_hook(i, status)],
            "merge_output_format": "mp4",
            "playlist_items": str(i + 1),
            "restrictfilenames": True,
        }
        with youtube_dl.YoutubeDL(opts) as ydl:
            try:
                ydl.download([bookmark.url])
            except youtube_dl.DownloadError:
                print('Error downloading video')
                continue

    return True


def create_single_page_archive(bookmark):
    maybe_create_bookmark_dir(str(bookmark.uuid))

    file_archive_uuid = uuid.uuid4()
    file_path = os.path.join(
        settings.MEDIA_ROOT, str(bookmark.uuid), str(file_archive_uuid) + ".html"
    )
    relative_file_path = os.path.join(
        str(bookmark.uuid), str(file_archive_uuid) + ".html"
    )
    download_single_page(bookmark.url, file_path)
    SinglePageArchive.objects.create(
        bookmark=bookmark, uuid=file_archive_uuid, rel_file_path=relative_file_path
    )


def create_video_archive(bookmark):
    maybe_create_bookmark_dir(str(bookmark.uuid))

    bookmark_file_path = os.path.join(settings.MEDIA_ROOT, str(bookmark.uuid))
    download_videos(bookmark, bookmark_file_path)
