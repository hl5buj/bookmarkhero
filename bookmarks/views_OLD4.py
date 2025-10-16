# bookmarks/views.py (After - 약 10줄!)
from rest_framework import viewsets
from .models import Bookmark
from .serializers import BookmarkSerializer

class BookmarkViewSet(viewsets.ModelViewSet):
    """
    북마크 ViewSet

    자동으로 제공되는 기능:
    - list: 북마크 목록
    - create: 북마크 생성
    - retrieve: 북마크 상세
    - update: 북마크 수정
    - partial_update: 북마크 부분 수정
    - destroy: 북마크 삭제
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

