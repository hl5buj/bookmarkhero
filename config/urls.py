# config/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,      # 로그인 (토큰 발급)
    TokenRefreshView,         # 토큰 갱신
    TokenVerifyView,          # 토큰 검증
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ===== JWT 인증 API =====
    # 로그인: username/password → Access + Refresh Token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 토큰 갱신: Refresh Token → 새 Access Token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 토큰 검증: 토큰이 유효한지 확인 (선택사항)
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # ===== 북마크 API =====
    path('api/', include('bookmarks.urls')),

    # ===== Browsable API 로그인 UI (개발용) =====
    path('api-auth/', include('rest_framework.urls')),
]

