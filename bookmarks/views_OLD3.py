# bookmarks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Bookmark
from .serializers import BookmarkSerializer

User = get_user_model()


class BookmarkListView(APIView):
    """
    북마크 목록 조회 및 생성 API (APIView 버전)

    APIView의 장점:
    - 메서드별로 함수 분리
    - request.data로 자동 파싱
    - Response로 자동 JSON 변환
    - CSRF 자동 처리
    """

    def get(self, request):
        """
        북마크 목록 조회 (GET /api/bookmarks/)

        실행 흐름:
        1. DB에서 모든 북마크 조회
        2. Serializer로 직렬화
        3. Response로 JSON 응답
        """
        # 1. DB 조회
        bookmarks = Bookmark.objects.all()

        # 2. Serializer로 변환 (many=True: 여러 객체)
        serializer = BookmarkSerializer(bookmarks, many=True)

        # 3. Response 반환
        # Response는 자동으로 JSON으로 변환하고
        # Content-Type: application/json 헤더를 설정합니다
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    def post(self, request):
        """
        새 북마크 생성 (POST /api/bookmarks/)

        실행 흐름:
        1. request.data에서 데이터 추출 (자동 파싱됨)
        2. Serializer로 검증
        3. 검증 통과 시 저장
        4. Response로 결과 반환
        """
        # 1. request.data
        # Django의 request.body를 파싱한 결과
        # Content-Type에 따라 자동으로 JSON/Form 데이터 파싱
        # JSONParser().parse(request) 대신 이것만 사용!

        # 2. Serializer 생성 및 검증
        serializer = BookmarkSerializer(data=request.data)

        if serializer.is_valid():
            # 검증 통과: 저장
            # owner는 임시로 첫 번째 사용자 지정
            user = User.objects.first()

            # save()에 추가 인자를 전달하면
            # validated_data에 추가되어 함께 저장됩니다
            bookmark = serializer.save(owner=user)

            # 생성된 객체를 다시 직렬화하여 응답
            return Response(
                BookmarkSerializer(bookmark).data,
                status=status.HTTP_201_CREATED  # 201
            )
        else:
            # 검증 실패: 에러 반환
            # Response는 serializer.errors를 자동으로 JSON으로 변환
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST  # 400
            )
