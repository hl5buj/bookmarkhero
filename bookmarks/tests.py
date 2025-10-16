# bookmarks/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Bookmark

User = get_user_model()


class BookmarkModelTests(TestCase):
    """북마크 모델 테스트"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_bookmark(self):
        """북마크 생성 테스트"""
        bookmark = Bookmark.objects.create(
            owner=self.user,
            title='Test Bookmark',
            url='https://example.com',
            description='Test description',
            is_public=True
        )
        self.assertEqual(bookmark.title, 'Test Bookmark')
        self.assertEqual(bookmark.owner, self.user)
        self.assertTrue(bookmark.is_public)

    def test_bookmark_str_method(self):
        """북마크 __str__ 메서드 테스트"""
        bookmark = Bookmark.objects.create(
            owner=self.user,
            title='Django Docs',
            url='https://docs.djangoproject.com'
        )
        self.assertEqual(str(bookmark), 'Django Docs')

    def test_bookmark_ordering(self):
        """북마크 정렬 테스트 (최신순)"""
        import time
        bookmark1 = Bookmark.objects.create(
            owner=self.user,
            title='First',
            url='https://first.com'
        )
        time.sleep(0.01)  # 타이밍 이슈 해결
        bookmark2 = Bookmark.objects.create(
            owner=self.user,
            title='Second',
            url='https://second.com'
        )
        bookmarks = Bookmark.objects.all()
        self.assertEqual(bookmarks[0], bookmark2)  # 최신이 먼저
        self.assertEqual(bookmarks[1], bookmark1)


class AuthAPITests(APITestCase):
    """인증 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/token/'
        self.me_url = '/api/auth/me/'

    def test_user_registration_success(self):
        """회원가입 성공 테스트"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')

    def test_user_registration_password_mismatch(self):
        """비밀번호 불일치 회원가입 실패 테스트"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'different123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_short_username(self):
        """짧은 사용자명 회원가입 실패 테스트"""
        data = {
            'username': 'ab',  # 3자 미만
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_username(self):
        """특수문자 포함 사용자명 실패 테스트"""
        data = {
            'username': 'user@#$',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """중복 이메일 회원가입 실패 테스트"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # 중복
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """로그인 성공 테스트"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_wrong_password(self):
        """잘못된 비밀번호 로그인 실패 테스트"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user_authenticated(self):
        """인증된 사용자 정보 조회 테스트"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_current_user_unauthenticated(self):
        """비인증 사용자 정보 조회 실패 테스트"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookmarkAPITests(APITestCase):
    """북마크 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.bookmark_url = '/api/bookmarks/'

    def test_create_bookmark_authenticated(self):
        """인증된 사용자 북마크 생성 테스트"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Django Documentation',
            'url': 'https://docs.djangoproject.com',
            'description': 'Official Django docs',
            'is_public': True
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Django Documentation')
        self.assertEqual(response.data['owner'], 'user1')

    def test_create_bookmark_unauthenticated(self):
        """비인증 사용자 북마크 생성 실패 테스트"""
        data = {
            'title': 'Test',
            'url': 'https://example.com',
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bookmark_duplicate_url(self):
        """중복 URL 북마크 생성 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        Bookmark.objects.create(
            owner=self.user1,
            title='First',
            url='https://example.com'
        )
        data = {
            'title': 'Second',
            'url': 'https://example.com',  # 중복
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bookmark_blocked_domain(self):
        """차단된 도메인 북마크 생성 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Spam Site',
            'url': 'https://spam.com/page',
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bookmark_short_title(self):
        """짧은 제목 북마크 생성 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'ab',  # 3자 미만
            'url': 'https://example.com',
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bookmark_html_title_cleaned(self):
        """HTML 태그 제거 테스트"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': '<b>Django</b> Documentation',
            'url': 'https://docs.djangoproject.com',
            'description': 'Test description',
            'is_public': False  # 공개가 아니면 설명이 필수가 아님
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Django Documentation')

    def test_create_public_bookmark_without_description(self):
        """공개 북마크 설명 없이 생성 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Test Bookmark',
            'url': 'https://example.com',
            'is_public': True,
            'description': ''  # 공개인데 설명 없음
        }
        response = self.client.post(self.bookmark_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_bookmarks_authenticated(self):
        """인증된 사용자 북마크 목록 조회 테스트"""
        self.client.force_authenticate(user=self.user1)
        Bookmark.objects.create(
            owner=self.user1,
            title='My Bookmark',
            url='https://my.com',
            is_public=False
        )
        Bookmark.objects.create(
            owner=self.user2,
            title='Public Bookmark',
            url='https://public.com',
            is_public=True
        )
        Bookmark.objects.create(
            owner=self.user2,
            title='Private Bookmark',
            url='https://private.com',
            is_public=False
        )
        response = self.client.get(self.bookmark_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 내 것 + 공개된 것

    def test_update_own_bookmark(self):
        """자신의 북마크 수정 테스트"""
        self.client.force_authenticate(user=self.user1)
        bookmark = Bookmark.objects.create(
            owner=self.user1,
            title='Original',
            url='https://original.com',
            description='Original description',
            is_public=False
        )
        data = {
            'title': 'Updated',
            'url': 'https://original.com',
            'description': 'Updated description',
            'is_public': False
        }
        response = self.client.put(f'{self.bookmark_url}{bookmark.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated')

    def test_delete_own_bookmark(self):
        """자신의 북마크 삭제 테스트"""
        self.client.force_authenticate(user=self.user1)
        bookmark = Bookmark.objects.create(
            owner=self.user1,
            title='To Delete',
            url='https://delete.com'
        )
        response = self.client.delete(f'{self.bookmark_url}{bookmark.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Bookmark.objects.filter(id=bookmark.id).exists())

    def test_recent_bookmarks(self):
        """최근 북마크 조회 테스트"""
        self.client.force_authenticate(user=self.user1)
        for i in range(15):
            Bookmark.objects.create(
                owner=self.user1,
                title=f'Bookmark {i}',
                url=f'https://example{i}.com'
            )
        response = self.client.get(f'{self.bookmark_url}recent/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)  # 최대 10개

    def test_my_bookmarks(self):
        """내 북마크만 조회 테스트"""
        self.client.force_authenticate(user=self.user1)
        Bookmark.objects.create(
            owner=self.user1,
            title='My Bookmark',
            url='https://my.com'
        )
        Bookmark.objects.create(
            owner=self.user2,
            title='Other Bookmark',
            url='https://other.com'
        )
        response = self.client.get(f'{self.bookmark_url}my_bookmarks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_bookmarks(self):
        """공개 북마크만 조회 테스트"""
        self.client.force_authenticate(user=self.user1)
        Bookmark.objects.create(
            owner=self.user1,
            title='Public 1',
            url='https://public1.com',
            is_public=True
        )
        Bookmark.objects.create(
            owner=self.user1,
            title='Private',
            url='https://private.com',
            is_public=False
        )
        response = self.client.get(f'{self.bookmark_url}public_bookmarks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_toggle_public_own_bookmark(self):
        """자신의 북마크 공개/비공개 토글 테스트"""
        self.client.force_authenticate(user=self.user1)
        bookmark = Bookmark.objects.create(
            owner=self.user1,
            title='Test',
            url='https://test.com',
            description='Test description',
            is_public=False
        )
        response = self.client.post(f'{self.bookmark_url}{bookmark.id}/toggle_public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_public'])

    def test_toggle_public_other_bookmark_forbidden(self):
        """다른 사용자의 북마크 토글 시도 실패 테스트"""
        self.client.force_authenticate(user=self.user1)
        bookmark = Bookmark.objects.create(
            owner=self.user2,
            title='Test',
            url='https://test.com',
            description='Test description',
            is_public=True
        )
        response = self.client.post(f'{self.bookmark_url}{bookmark.id}/toggle_public/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BookmarkSerializerTests(APITestCase):
    """북마크 시리얼라이저 추가 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.bookmark_url = '/api/bookmarks/'

    def test_update_bookmark_same_url_allowed(self):
        """자신의 북마크 수정 시 같은 URL 허용 테스트"""
        self.client.force_authenticate(user=self.user)
        bookmark = Bookmark.objects.create(
            owner=self.user,
            title='Original',
            url='https://example.com',
            description='Original description',
            is_public=False
        )
        # 같은 URL로 제목만 변경
        data = {
            'title': 'Updated Title',
            'url': 'https://example.com',  # 같은 URL
            'description': 'Updated description',
            'is_public': False
        }
        response = self.client.put(f'{self.bookmark_url}{bookmark.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
