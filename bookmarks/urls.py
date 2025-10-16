# bookmarks/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookmarkViewSet, AuthViewSet

router = DefaultRouter()

# 북마크 API
router.register('bookmarks', BookmarkViewSet, basename='bookmark')

# 인증 API
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]

# 생성되는 URL:
# POST   /api/auth/register/     → 회원가입
# GET    /api/auth/me/           → 내 정보 조회
#
# GET    /api/bookmarks/         → 북마크 목록
# POST   /api/bookmarks/         → 북마크 생성
# ... (나머지 CRUD)



