# bookmarks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # FBV (Step 3)
    # path('bookmarks/', views.bookmark_list, name='bookmark-list'),

    # APIView (Step 4)
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmark-list'),
    # .as_view(): 클래스 뷰를 함수 뷰로 변환
]

