from archiver.tasks import create_single_page_archive, create_video_archive
from .models import Bookmark, Tag
from django_q.tasks import async_task

from urllib.request import urlopen, Request
import lxml.html
from lxml import etree
import tldextract
import re
from datetime import datetime

SEARCH_SINCE_RE = re.compile(r'\bsince:(\d{4}-\d{2}-\d{2})\b')
SEARCH_UNTIL_RE = re.compile(r'\buntil:(\d{4}-\d{2}-\d{2})\b')
SEARCH_TAGS_RE = re.compile(r'\btags:([\w,]+)\b')

def create_bookmark(title, url, tags_str, to_read, user):
    tags = []
    tags_str = tags_str.split(",")
    for tag_str in tags_str:
        if tag_str:
            tag, _ = Tag.objects.get_or_create(word=tag_str.strip(), user=user)
            tags.append(tag)

    b = Bookmark.objects.create(title=title, url=url, user=user, to_read=to_read)
    for tag in tags:
        b.tags.add(tag)

    b.save()

    async_task(create_single_page_archive, b)
    async_task(create_video_archive, b)


def get_page_title(url):
    req = Request(url)
    if tldextract.extract(url).domain == 'twitter':
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://google.com/bot.html)")
    page = urlopen(req)
    p = lxml.html.parse(page)

    title_html = p.find(".//title")
    if title_html is not None:
        return title_html.text
    else:
        return url


def get_since_query(query):
    since = None
    m = SEARCH_SINCE_RE.search(query)
    if m is not None:
        since = datetime.strptime(m.group(1), '%Y-%m-%d')
        query = query[:m.span()[0]] + query[m.span()[1]:]

    return since, query


def get_until_query(query):
    until = None
    m = SEARCH_UNTIL_RE.search(query)
    if m is not None:
        until = datetime.strptime(m.group(1), '%Y-%m-%d')
        query = query[:m.span()[0]] + query[m.span()[1]:]

    return until, query


def get_tags_query(query):
    tags = []
    m = SEARCH_TAGS_RE.search(query)
    if m is not None:
        tags = m.group(1).split(',')
        tags = [t for t in tags if t]
        query = query[:m.span()[0]] + query[m.span()[1]:]

    return tags, query
