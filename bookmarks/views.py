from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q

from django_q.tasks import async_task

import csv
import re

from .models import Bookmark, Tag
from .forms import BookmarkForm, ImportFileForm
from . import utils

def home(request):
    if request.user.is_authenticated:
        return redirect(reverse('bm'))

    return render(request, 'home.html', {'login_form': AuthenticationForm()})


@login_required
def bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-date_time_added')
    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bookmarks.html', {'bookmarks': page_obj, 'bmform': BookmarkForm(), 'import_html_form': ImportFileForm()})

@login_required
def bookmarks_to_read(request):
    bookmarks = Bookmark.objects.filter(user=request.user, to_read=True).order_by('-date_time_added')
    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bookmarks_to_read.html', {'bookmarks': page_obj, 'bmform': BookmarkForm(), 'import_html_form': ImportFileForm()})
    

@login_required
def bookmark_add(request):
    print(request.method)
    if request.method == 'POST':
        bookmark_form = BookmarkForm(request.POST)
        if bookmark_form.is_valid():
            if bookmark_form.cleaned_data['title'] == '':
                title = utils.get_page_title(bookmark_form.cleaned_data['url'])
            else:
                title = bookmark_form.cleaned_data['title']
            
            utils.create_bookmark(
                title,
                bookmark_form.cleaned_data['url'],
                bookmark_form.cleaned_data['tags'],
                bookmark_form.cleaned_data['to_read'],
                request.user
            )
            
            if bookmark_form.cleaned_data['auto_close']:
                return render(request, 'close.html')
            else:
                return HttpResponseRedirect(reverse('bm'))
            
    else:
        data = {}
        if 'url' in request.GET:
            data['url'] = request.GET.get('url')

            if 'title' in request.GET:
                data['title'] = request.GET.get('title')
            else:
                data['title'] = utils.get_page_title(data['url'])

        if 'auto_close' in request.GET:
            data['auto_close'] = request.GET.get('auto_close')

        if 'to_read' in request.GET and request.GET.get('to_read'):
            utils.create_bookmark(data['title'], data['url'], '', True, request.user)
            return render(request, 'close.html')

        bookmark_form = BookmarkForm(initial=data)
        

    return render(request, 'bookmark_add.html', {'bookmark_form': bookmark_form})


@login_required
def bookmark_edit(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('bm'))

    bookmark_data= {
        'title': bookmark.title,
        'url': bookmark.url,
        'tags': ','.join([tag.word for tag in bookmark.tags.all()]),
        'to_read': bookmark.to_read
    }
    
    if request.method == 'POST':
        bookmark_form = BookmarkForm(request.POST, initial=bookmark_data)
        if bookmark_form.is_valid():
            if not bookmark_form.has_changed():
                return HttpResponseRedirect(reverse('bm'))

            to_update = set(bookmark_form.changed_data)

            if 'title' in to_update:
                title = bookmark_form.cleaned_data['title']
                bookmark.title = title

            if 'url' in to_update:
                url = bookmark_form.cleaned_data['url']
                bookmark.url = url

            if 'tags' in to_update:
                tags_str = bookmark_form.cleaned_data['tags']
                tags = set([tag_str.strip() for tag_str in tags_str.split(',')])
                tags.discard('')
                db_tags = set([tag.word for tag in bookmark.tags.all()])
                    
                for tag_str in tags.difference(db_tags):
                    tag, _ = Tag.objects.get_or_create(word=tag_str, user=request.user)
                    bookmark.tags.add(tag)
                        
                for tag_str in db_tags.difference(tags):
                    tag = Tag.objects.get(word=tag_str, user=request.user)
                    bookmark.tags.remove(tag)

            if 'to_read' in to_update:
                to_read = bookmark_form.cleaned_data['to_read']
                bookmark.to_read = to_read

            bookmark.save()           
            return HttpResponseRedirect(reverse('bm'))

    else:
        bookmark_form = BookmarkForm(initial=bookmark_data)
        return render(request, 'bookmark_edit.html', {'bookmark_form': bookmark_form})


@login_required
def set_read(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id)
        bookmark.to_read = False
        bookmark.save()

    except ObjectDoesNotExist:
        pass

    return HttpResponseRedirect(reverse('bm'))


@login_required
def set_unread(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id)
        bookmark.to_read = True
        bookmark.save()

    except ObjectDoesNotExist:
        pass

    return HttpResponseRedirect(reverse('bm'))

    
@login_required
def bookmark_delete(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
        bookmark.delete()
    except ObjectDoesNotExist:
        pass

    return HttpResponseRedirect(reverse('bm'))


@login_required
def tag_view(request, word):
    try:
        tag = Tag.objects.get(word=word)
        bookmarks = tag.bookmarks.all().order_by('-date_time_added')
    except ObjectDoesNotExist:
        bookmarks = []

    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tag.html', {'bookmarks': page_obj, 'word': word})

@login_required
def untagged_view(request):
    bookmarks = Bookmark.objects.filter(tags=None)

    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tag.html', {'bookmarks': page_obj, 'word': 'untagged'})


@login_required
def help_view(request):
    return render(request, 'help.html')


@login_required
def search_view(request):
    bookmarks = request.user.bookmarks
    query = request.GET.get('query')
    original_query = query
    
    q_object = Q()
    
    since_datetime, query = utils.get_since_query(query)
    if since_datetime is not None:
        q_object &= Q(date_time_added__gte=since_datetime)
        
    until_datetime, query = utils.get_until_query(query)
    if until_datetime is not None:
        q_object &= Q(date_time_added__lte=until_datetime)

    filtered_bookmarks = bookmarks.filter(q_object)

    if query and not query.isspace():
        filtered_bookmarks = \
            filtered_bookmarks.annotate(search=SearchVector('title')) \
                              .filter(search=SearchQuery(query))

    filtered_bookmarks = filtered_bookmarks.distinct('id')

    paginator = Paginator(filtered_bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {'bookmarks': page_obj, 'query': original_query})

@login_required
def import_html(request):
    if request.method == "POST":
        form = ImportFileForm(request.POST, files=request.FILES)

        if form.is_valid(): 
            html_file = request.FILES['html']
            root = lxml.html.fromstring(html_file.read())
            for dt in root.findall('.//dt'):
                bookmark_a = dt.find('a')
                if bookmark_a is None:
                    continue
                
                title = bookmark_a.text
                url = bookmark_a.get('href')
                
                tags_str = bookmark_a.get('tags')
                tags_str_list = []
                tags = []
                if tags_str is not None:
                    tags_str_list = tags_str.split(',')
                
                for tag_str in tags_str_list:
                    if tag_str:
                        tag, _ = Tag.objects.get_or_create(word=tag_str.strip(), user=request.user)
                        tags.append(tag)
                        
                b = Bookmark.objects.create(title=title, url=url, user=request.user)
                for tag in tags:
                    b.tags.add(tag)

                b.save()

            return HttpResponseRedirect(reverse('home'))

    else:
        return render(request, 'import_html.html', {'import_html_form': ImportFileForm})

@login_required
def export_csv(request):
    bookmarks = Bookmark.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookmarks.csv"'

    writer = csv.writer(response)

    for b in bookmarks:
        tags_str = ','.join([tag.word for tag in b.tags.all()])
        writer.writerow([b.url, b.title, b.to_read, b.date_time_added, tags_str])

    return response
    
            
def login_page(request):
    incorrect_password = False
    if request.method == 'POST':
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = authenticate(
                username=login_form.cleaned_data['username'],
                password=login_form.cleaned_data['password']
            )
            
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('bm'))

            else:
                valid_password = True

    else:
        login_form = AuthenticationForm()

    return render(request, 'login.html', {'login_form': login_form, 'incorrect_password': incorrect_password})


def signup(request):
    if request.method == 'POST':
        signup_form = UserCreationForm(data=request.POST)
        if signup_form.is_valid():
            signup_form.save()
            return HttpResponseRedirect(reverse('bm'))

    else:
        signup_form = UserCreationForm()

    return render(request, 'signup.html', {'signup_form': signup_form})

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))
    
