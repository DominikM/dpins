from .models import Bookmark, Tag

def create_bookmark(title, url, tags_str, to_read, user):
    tags = []
    tags_str = tags_str.split(',')
    for tag_str in tags_str:
        if tag_str:
            tag, _ = Tag.objects.get_or_create(word=tag_str.strip(), user=user)
            tags.append(tag)

    b = Bookmark.objects.create(title=title, url=url, user=user, to_read=to_read)
    for tag in tags:
        b.tags.add(tag)
                
    b.save()
