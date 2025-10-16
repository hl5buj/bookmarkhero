# bookmarks/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Bookmark
from .serializers import BookmarkSerializer

@csrf_exempt
def bookmark_list(request):
    """
    Serializer를 사용한 버전
    코드가 얼마나 간결해졌는지 확인하세요!
    """

    if request.method == 'GET':
        # ===== 목록 조회 =====
        bookmarks = Bookmark.objects.all()

        # Serializer로 변환 (many=True: 여러 객체 직렬화)
        serializer = BookmarkSerializer(bookmarks, many=True)

        # 끝! 이게 전부입니다.
        return JsonResponse({
            'count': len(serializer.data),
            'results': serializer.data
        })

    elif request.method == 'POST':
        # ===== 새 북마크 생성 =====

        # JSON 파싱
        data = JSONParser().parse(request)

        # Serializer로 검증 + 저장
        serializer = BookmarkSerializer(data=data)

        if serializer.is_valid():
            # 검증 통과: 저장
            # owner는 임시로 첫 번째 사용자 지정
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.first()

            bookmark = serializer.save(owner=user)

            # 생성된 객체를 다시 직렬화
            return JsonResponse(
                BookmarkSerializer(bookmark).data,
                status=201
            )
        else:
            # 검증 실패: 에러 반환
            return JsonResponse(
                {'errors': serializer.errors},
                status=400
            )

    return JsonResponse({'error': 'Method not allowed'}, status=405)
