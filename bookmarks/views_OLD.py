# bookmarks/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Bookmark
import json

@csrf_exempt  # 테스트를 위해 CSRF 비활성화 (실무에서는 절대 사용 금지)
def bookmark_list(request):
    """
    북마크 목록 조회 및 생성 API

    이 코드의 문제점들을 직접 경험해보세요:
    1. JSON 변환을 수동으로 해야 함
    2. 검증 로직이 복잡함
    3. 에러 처리가 일관성 없음
    """

    if request.method == 'GET':
        # ===== 목록 조회 =====

        # 1단계: DB에서 데이터 가져오기
        bookmarks = Bookmark.objects.all()

        # 2단계: 수동으로 JSON 형태로 변환
        # 각 필드를 일일이 지정해야 함
        data = []
        for bookmark in bookmarks:
            data.append({
                'id': bookmark.id,
                'title': bookmark.title,
                'url': bookmark.url,
                'description': bookmark.description,
                'owner': bookmark.owner.username,
                'created_at': bookmark.created_at.isoformat(),  # datetime을 문자열로 변환
            })

        # 3단계: JSON 응답 반환
        return JsonResponse({
            'count': len(data),
            'results': data
        })

    elif request.method == 'POST':
        # ===== 새 북마크 생성 =====

        try:
            # 1단계: 요청 본문에서 JSON 파싱
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)

        # 2단계: 데이터 추출
        title = body.get('title')
        url = body.get('url')
        description = body.get('description', '')

        # 3단계: 수동 검증 (매우 번거로움!)
        errors = {}

        if not title:
            errors['title'] = ['이 필드는 필수입니다.']
        elif len(title) > 200:
            errors['title'] = ['제목은 200자를 초과할 수 없습니다.']

        if not url:
            errors['url'] = ['이 필드는 필수입니다.']
        elif not url.startswith(('http://', 'https://')):
            errors['url'] = ['올바른 URL 형식이 아닙니다.']

        # 중복 URL 체크
        if url and Bookmark.objects.filter(url=url).exists():
            errors['url'] = ['이 URL은 이미 저장되어 있습니다.']

        # 검증 실패 시 에러 반환
        if errors:
            return JsonResponse({
                'errors': errors
            }, status=400)

        # 4단계: DB에 저장
        # owner를 하드코딩 (실제로는 request.user 사용)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.first()  # 임시로 첫 번째 사용자 사용

        bookmark = Bookmark.objects.create(
            title=title,
            url=url,
            description=description,
            owner=user
        )

        # 5단계: 생성된 객체를 다시 JSON으로 변환 (또 반복!)
        return JsonResponse({
            'id': bookmark.id,
            'title': bookmark.title,
            'url': bookmark.url,
            'description': bookmark.description,
            'owner': bookmark.owner.username,
            'created_at': bookmark.created_at.isoformat(),
        }, status=201)

    # 지원하지 않는 메서드
    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)

