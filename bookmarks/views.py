from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector, SearchQuery

from .models import Bookmark, Tag
from .forms import BookmarkForm, SimpleSearchForm


def home(request):
    if request.user.is_authenticated:
        return redirect(reverse('bm'))

    return render(request, 'home.html', {'login_form': AuthenticationForm()})


@login_required
def bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bookmarks.html', {'bookmarks': page_obj, 'bmform': BookmarkForm()})
    

@login_required
def bookmark_add(request):
    print(request.method)
    if request.method == 'POST':
        bookmark_form = BookmarkForm(request.POST)
        if bookmark_form.is_valid():
            title = bookmark_form.cleaned_data['title']
            url = bookmark_form.cleaned_data['url']
            tags_str = bookmark_form.cleaned_data['tags']

            tags = []
            tags_str = tags_str.split(',')
            for tag_str in tags_str:
                if tag_str:
                    tag, _ = Tag.objects.get_or_create(word=tag_str.strip(), user=request.user)
                    tags.append(tag)

            b = Bookmark.objects.create(title=title, url=url, user=request.user)
            for tag in tags:
                b.tags.add(tag)
                
            b.save()

            if bookmark_form.cleaned_data['auto_close']:
                return render(request, 'close.html')
            else:
                return HttpResponseRedirect(reverse('bm'))
            
    else:
        data = {}
        if 'title' in request.GET:
            data['title'] = request.GET.get('title')

        if 'url' in request.GET:
            data['url'] = request.GET.get('url')

        if 'auto_close' in request.GET:
            data['auto_close'] = request.GET.get('auto_close')

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
        'tags': ','.join([tag.word for tag in bookmark.tags.all()])
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
                db_tags = set([tag.name for tag in bookmark.tags.all()])
                    
                for tag_str in tags.difference(db_tags):
                    tag = Tag.objects.get_or_create(name=tag_str)
                    bookmark.tags.add(tag)
                        
                for tag_str in db_tags.difference(tags):
                    tag = Tag.objects.get(name=tag_str)
                    bookmark.tags.remove(tag)

            bookmark.save()           
            return HttpResponseRedirect(reverse('bm'))

    else:
        bookmark_form = BookmarkForm(initial=bookmark_data)
        return render(request, 'bookmark_edit.html', {'bookmark_form': bookmark_form})

    
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
        bookmarks = tag.bookmarks.all()
    except ObjectDoesNotExist:
        bookmarks = []

    paginator = Paginator(bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tag.html', {'bookmarks': page_obj})


@login_required
def search_view(request):
    bookmarks = request.user.bookmarks
    query = request.GET.get('query')
    filtered_bookmarks = \
        bookmarks.annotate(search=SearchVector('title', 'url', 'tags__word')) \
                         .filter(search=SearchQuery(query)) \
                         .distinct('id')

    print(len(filtered_bookmarks))
    
    paginator = Paginator(filtered_bookmarks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {'bookmarks': page_obj, 'query': query})
            
            


@login_required
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
    
