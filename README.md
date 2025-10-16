# BookmarkHero

Django REST Framework 기반 북마크 관리 서비스

## 📋 프로젝트 개요

BookmarkHero는 사용자가 웹 북마크를 저장하고 관리할 수 있는 REST API 서비스입니다.
JWT 인증을 사용하며, 공개/비공개 북마크 관리, HTML 태그 제거, 도메인 차단 등의 보안 기능을 제공합니다.

## ✨ 주요 기능

### 인증
- 회원가입 (username, email, password 검증)
- JWT 기반 로그인/토큰 갱신
- 사용자 정보 조회

### 북마크 관리
- CRUD 기본 기능 (생성, 조회, 수정, 삭제)
- 공개/비공개 설정
- 최근 북마크 조회
- 내 북마크 필터링
- 공개 북마크 목록

### 보안
- HTML 태그 자동 제거 (XSS 방어)
- 도메인 차단 기능 (spam.com, malicious.com)
- URL 중복 체크
- 권한 기반 접근 제어

## 🛠 기술 스택

- **Backend**: Django 5.2.7, Django REST Framework 3.16.1
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Database**: SQLite (개발), PostgreSQL/MySQL 권장 (프로덕션)
- **Python**: 3.11+

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd bookmarkhero
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install django==5.2.7
pip install djangorestframework==3.16.1
pip install djangorestframework-simplejwt==5.5.1
```

### 4. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

### 5. 관리자 계정 생성
```bash
python manage.py createsuperuser
```

### 6. 개발 서버 실행
```bash
python manage.py runserver
```

서버가 `http://127.0.0.1:8000/`에서 실행됩니다.

## 🌐 API 엔드포인트

### 인증 API

#### 회원가입
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "test1234",
  "password_confirm": "test1234",
  "first_name": "John",
  "last_name": "Doe"
}
```

**응답:**
```json
{
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com"
  },
  "tokens": {
    "access": "eyJhbGciOi...",
    "refresh": "eyJzdWIiOi..."
  }
}
```

#### 로그인
```http
POST /api/token/
Content-Type: application/json

{
  "username": "john",
  "password": "test1234"
}
```

**응답:**
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJzdWIiOi..."
}
```

#### 토큰 갱신
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJzdWIiOi..."
}
```

#### 내 정보 조회
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### 북마크 API

#### 북마크 목록 조회
```http
GET /api/bookmarks/
Authorization: Bearer <access_token>
```

**응답:** 자신의 북마크 + 공개 북마크 목록

#### 북마크 생성
```http
POST /api/bookmarks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Django Documentation",
  "url": "https://docs.djangoproject.com",
  "description": "Official Django docs",
  "is_public": true
}
```

#### 북마크 상세 조회
```http
GET /api/bookmarks/{id}/
Authorization: Bearer <access_token>
```

#### 북마크 수정
```http
PUT /api/bookmarks/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "url": "https://docs.djangoproject.com",
  "description": "Updated description",
  "is_public": false
}
```

#### 북마크 삭제
```http
DELETE /api/bookmarks/{id}/
Authorization: Bearer <access_token>
```

#### 최근 북마크 10개
```http
GET /api/bookmarks/recent/
Authorization: Bearer <access_token>
```

#### 내 북마크만 조회
```http
GET /api/bookmarks/my_bookmarks/
Authorization: Bearer <access_token>
```

#### 공개 북마크 조회
```http
GET /api/bookmarks/public_bookmarks/
Authorization: Bearer <access_token>
```

#### 공개/비공개 토글
```http
POST /api/bookmarks/{id}/toggle_public/
Authorization: Bearer <access_token>
```

## 🧪 테스트

### 전체 테스트 실행
```bash
python manage.py test bookmarks
```

### 상세 출력으로 테스트
```bash
python manage.py test bookmarks --verbosity=2
```

### 테스트 결과
```
✅ 28개 테스트 모두 통과

- 모델 테스트: 3개
- 인증 API 테스트: 9개
- 북마크 API 테스트: 15개
- 시리얼라이저 테스트: 1개
```

## 🔒 보안 기능

### 1. JWT 인증
- Access Token: 60분 유효
- Refresh Token: 7일 유효
- Token 자동 갱신 및 이전 토큰 무효화

### 2. 입력 검증
- **회원가입**
  - username: 3자 이상, 영문/숫자/언더스코어만 허용
  - email: 중복 체크
  - password: 8자 이상, 영문+숫자 조합 필수

- **북마크**
  - title: 3자 이상, HTML 태그 자동 제거
  - url: 중복 체크, 도메인 차단 목록 검증
  - 공개 북마크는 설명 필수

### 3. 권한 제어
- 자신의 북마크만 수정/삭제 가능
- 관리자: 모든 북마크 조회 가능
- 일반 사용자: 자신의 북마크 + 공개 북마크만 조회

### 4. XSS 방어
- HTML 태그 자동 제거 (정규표현식)
- 안전한 텍스트만 저장

## 📊 데이터 모델

### User (Django 기본 모델)
- username
- email
- password
- first_name
- last_name

### Bookmark
- owner (ForeignKey → User)
- title (CharField, max_length=200)
- url (URLField)
- description (TextField, optional)
- is_public (BooleanField, default=True)
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

## 🎨 관리자 페이지

Django Admin 페이지 (`/admin/`)에서 북마크 관리 가능:
- 제목, URL, 소유자, 공개여부, 생성일 표시
- 공개여부, 생성일, 소유자로 필터링
- 제목, URL, 설명으로 검색

## 📝 개발 환경 설정

현재 `settings.py`는 개발 환경용입니다. 다음 설정들은 개발 편의를 위한 것입니다:

```python
DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY = 'django-insecure-...'  # 자동 생성된 키
```

## 🚀 프로덕션 배포 전 체크리스트

프로덕션 환경 배포 시 `settings.py`에서 다음 항목 변경 필요:

```python
# 보안 설정
DEBUG = False
SECRET_KEY = '새로운-긴-랜덤-키'
ALLOWED_HOSTS = ['yourdomain.com']

# HTTPS 설정
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# 데이터베이스
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bookmarkhero',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 정적 파일
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## 📁 프로젝트 구조

```
bookmarkhero/
├── bookmarks/              # 북마크 앱
│   ├── migrations/         # 데이터베이스 마이그레이션
│   ├── admin.py           # 관리자 페이지 설정
│   ├── apps.py            # 앱 설정
│   ├── models.py          # Bookmark 모델
│   ├── serializers.py     # DRF 시리얼라이저
│   ├── tests.py           # 테스트 코드 (28개)
│   ├── urls.py            # 북마크 API 라우팅
│   └── views.py           # API ViewSets
├── config/                # 프로젝트 설정
│   ├── settings.py        # Django 설정
│   ├── urls.py            # 전역 URL 설정
│   ├── wsgi.py           # WSGI 설정
│   └── asgi.py           # ASGI 설정
├── manage.py              # Django 관리 스크립트
├── db.sqlite3            # SQLite 데이터베이스
└── README.md             # 이 파일
```

## 🔧 문제 해결

### 테스트 실패 시
```bash
# 데이터베이스 초기화
python manage.py flush

# 마이그레이션 재실행
python manage.py migrate

# 테스트 재실행
python manage.py test bookmarks
```

### 의존성 문제 시
```bash
# 패키지 재설치
pip install --upgrade django djangorestframework djangorestframework-simplejwt
```

## 📚 참고 자료

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)

## 📄 라이선스

이 프로젝트는 학습 목적으로 만들어졌습니다.

## 👨‍💻 개발자

프로젝트 개발 및 테스트 완료: 2025-10-16

---

**테스트 상태**: ✅ 28/28 통과 (100%)
**프로덕션 준비**: ⚠️ 보안 설정 추가 필요
