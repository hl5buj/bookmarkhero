# bookmarks/urls.py (After - 약 5줄!)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookmarkViewSet

router = DefaultRouter()
router.register('bookmarks', BookmarkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


