# bookmarks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('bookmarks/', views.bookmark_list, name='bookmark-list'),
]
