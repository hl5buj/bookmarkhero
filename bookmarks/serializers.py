# bookmarks/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Bookmark

User = get_user_model()

class BookmarkSerializer(serializers.Serializer):
    """
    커스텀 검증이 추가된 Serializer
    """
    # 필드 정의 (Step 3과 동일)
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    url = serializers.URLField()
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=True)
    owner = serializers.CharField(source='owner.username', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_url(self, value):
        """
        URL 필드 커스텀 검증

        실행 시점:
        - serializer.is_valid()가 호출될 때
        - URLField의 기본 검증(URL 형식) 통과 후

        Args:
            value (str): 사용자가 입력한 URL
                        예: "https://docs.djangoproject.com"

        Returns:
            str: 검증을 통과한 URL
                 반드시 return 해야 합니다!

        Raises:
            serializers.ValidationError: 검증 실패 시
        """

        # ===== 검증 1: 중복 URL 체크 =====
        # "같은 URL이 이미 저장되어 있나요?"

        # 데이터베이스에서 같은 URL 찾기
        queryset = Bookmark.objects.filter(url=value)
        # queryset: 같은 URL을 가진 북마크들

        # 중요한 케이스: 수정 vs 생성
        if self.instance:
            # self.instance가 있음 = 기존 북마크를 수정 중
            # 예: id=5인 북마크의 URL을 수정
            #     원래 URL: "https://old.com"
            #     새 URL: "https://new.com"

            # 문제: 만약 새 URL도 "https://old.com"이면?
            # → 자기 자신과 중복! 하지만 이건 허용해야 함

            # 해결: 현재 수정 중인 북마크는 제외
            queryset = queryset.exclude(pk=self.instance.pk)
            # pk: Primary Key (id와 같은 의미)
            # "나(self.instance) 말고 다른 북마크 중에 중복 있어?"
        else:
            # self.instance가 None = 새로 생성 중
            # 모든 북마크와 비교
            pass

        # 중복 체크
        if queryset.exists():
            # exists(): "하나라도 있으면 True"
            raise serializers.ValidationError(
                "이 URL은 이미 저장되어 있습니다."
            )
            # 여기서 함수 종료! return까지 가지 않음

        # ===== 검증 2: 도메인 차단 =====
        # "스팸 사이트는 막아야죠"

        # URL에서 도메인만 추출
        from urllib.parse import urlparse
        # urlparse: URL을 여러 부분으로 쪼개는 함수

        parsed = urlparse(value)
        # 예: "https://spam.com/page?id=1"
        # → scheme: "https"
        # → netloc: "spam.com"  ← 우리가 필요한 부분!
        # → path: "/page"
        # → query: "id=1"

        domain = parsed.netloc
        # domain = "spam.com"

        # 차단할 도메인 목록
        blocked_domains = ['spam.com', 'malicious.com']

        if domain in blocked_domains:
            raise serializers.ValidationError(
                f"이 도메인({domain})은 차단되었습니다."
            )

        # ===== 모든 검증 통과! =====
        # 반드시 값을 return!
        return value
        # 이 값이 validated_data['url']에 저장됨

    def validate_title(self, value):
        """
        제목 필드 커스텀 검증

        목적:
        1. HTML 태그 제거 (보안)
        2. 최소 길이 확인 (품질)

        Args:
            value (str): 사용자가 입력한 제목
                        예: "<script>alert('xss')</script>Django"

        Returns:
            str: 정제된 제목
                 예: "Django"
        """

        # ===== HTML 태그 제거 =====
        import re
        # re: 정규표현식 모듈

        clean_title = re.sub(r'<[^>]+>', '', value)
        # re.sub(패턴, 대체할문자, 원본)
        # r'<[^>]+>': "<"로 시작해서 ">"로 끝나는 모든 것
        # '': 빈 문자열로 대체 (= 삭제)

        # 예시:
        # value = "<b>Django</b> <script>...</script>문서"
        # clean_title = "Django 문서"

        # ===== 최소 길이 확인 =====
        # 공백 제거 후 체크
        if len(clean_title.strip()) < 3:
            # strip(): 앞뒤 공백 제거
            # "   hi   " → "hi"

            raise serializers.ValidationError(
                "제목은 HTML 태그를 제외하고 3자 이상이어야 합니다."
            )
            # 왜 3자?
            # - "ㅋ", "ㄱ" 같은 의미 없는 제목 방지
            # - 실무에서는 서비스 특성에 맞게 조정

        # ===== 정제된 제목 반환 =====
        # 원본이 아닌 정제된 값을 반환!
        return clean_title
        # 이제 DB에는 HTML 태그가 없는 제목이 저장됨

    def validate(self, attrs):
        """
        객체 레벨 검증
        여러 필드의 관계를 검증합니다

        실행 시점:
        - 모든 필드 레벨 검증이 통과한 후
        - is_valid() 내에서 마지막에 실행

        Args:
            attrs (dict): 검증을 통과한 모든 필드 데이터
                         {
                             'title': 'React 공식 문서',
                             'url': 'https://react.dev',
                             'description': '',
                             'is_public': True
                         }

        Returns:
            dict: 검증된 attrs
                  반드시 return 해야 함!

        Raises:
            serializers.ValidationError: 검증 실패 시
        """

        # ===== 비즈니스 규칙 검증 =====
        # 규칙: "공개 북마크는 설명이 필수"

        # attrs에서 값 가져오기
        is_public = attrs.get('is_public')
        # .get('is_public'): is_public 키의 값
        # 없으면 None 반환 (KeyError 안 남)

        description = attrs.get('description')

        # 조건 확인
        if is_public and not description:
            # is_public이 True이고
            # description이 빈 문자열이거나 None이면

            raise serializers.ValidationError(
                "공개 북마크는 설명이 필수입니다."
            )
            # 주의: 여기서 raise하면 특정 필드가 아닌
            #      "non_field_errors"에 에러가 들어감

        # ===== 검증 통과 =====
        # attrs를 수정할 수도 있음
        return attrs
        # 이 attrs가 validated_data가 됨

    def create(self, validated_data):
        return Bookmark.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.url = validated_data.get('url', instance.url)
        instance.description = validated_data.get('description', instance.description)
        instance.is_public = validated_data.get('is_public', instance.is_public)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    """
    사용자 조회용 Serializer
    비밀번호는 제외
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    회원가입용 Serializer

    비즈니스 요구사항:
    - username: 3자 이상 (중복 체크는 ModelSerializer가 자동 처리)
    - email: 필수 (중복 체크)
    - password: 8자 이상, 영문+숫자 조합
    - password_confirm: password와 일치해야 함
    """

    # password 필드를 ModelSerializer가 자동 생성하지만
    # write_only=True를 명시적으로 설정
    password = serializers.CharField(
        write_only=True,     # 응답에 포함 안 됨
        min_length=8,        # 최소 8자
        style={'input_type': 'password'}  # Browsable API에서 password 입력란으로 표시
    )

    # 비밀번호 확인 필드 (모델에는 없는 필드)
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},  # email을 필수로
        }

    def validate_username(self, value):
        """
        username 필드 검증

        실행 시점: is_valid() 호출 시
        ModelSerializer가 이미 unique 체크를 하지만
        추가 비즈니스 로직이 필요하면 여기에 작성
        """
        # 최소 길이 체크
        if len(value) < 3:
            raise serializers.ValidationError(
                "사용자명은 3자 이상이어야 합니다."
            )

        # 특수문자 체크 (선택사항)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "사용자명은 영문, 숫자, 언더스코어만 가능합니다."
            )

        return value

    def validate_email(self, value):
        """
        email 중복 체크
        """
        # ModelSerializer가 자동으로 unique 체크를 하지만
        # 더 친절한 에러 메시지를 위해 명시적으로 작성
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "이미 사용 중인 이메일입니다."
            )

        return value

    def validate_password(self, value):
        """
        password 복잡도 검증
        """
        import re

        # 영문 포함 확인
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError(
                "비밀번호는 영문을 포함해야 합니다."
            )

        # 숫자 포함 확인
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                "비밀번호는 숫자를 포함해야 합니다."
            )

        # Django의 기본 비밀번호 검증도 사용 (선택사항)
        from django.contrib.auth.password_validation import validate_password as django_validate
        try:
            django_validate(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        return value

    def validate(self, attrs):
        """
        객체 레벨 검증
        password와 password_confirm 일치 확인
        """
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')  # pop으로 제거 (모델에 없는 필드)

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': '비밀번호가 일치하지 않습니다.'
            })

        return attrs

    def create(self, validated_data):
        """
        사용자 생성

        중요: 비밀번호는 해시화하여 저장!
        User.objects.create() 대신 create_user() 사용
        """
        # create_user()는 자동으로 비밀번호를 해시화해 준다
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # 자동 해시화됨
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        return user

