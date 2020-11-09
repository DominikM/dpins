"""dpins URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('bm/', views.bookmarks, name='bm'),
    path('add/', views.bookmark_add, name='bookmark_add'),
    path('edit/<bookmark_id>/', views.bookmark_edit, name='bookmark_edit'),
    path('delete/<bookmark_id>/', views.bookmark_delete, name='bookmark_delete'),
    path('tag/<word>/', views.tag_view, name='tag'),
    path('search/', views.search_view, name='search'),
    path('import_html/', views.import_html, name='import_html'),
    path('set_read/<bookmark_id>', views.set_read, name='set_read'),
    path('set_unread/<bookmark_id>', views.set_unread, name='set_unread'),
    path('to_read/', views.bookmarks_to_read, name='bookmarks_to_read')
]
