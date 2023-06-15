import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserDetailSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions

# from .tokens import account_activation_token
# from django.utils.http               import urlsafe_base64_encode,urlsafe_base64_decode
# from django.core.mail                import EmailMessage
# from django.utils.encoding           import force_bytes, force_text
# from django.http import HttpResponseRedirect
# from rest_framework.permissions import AllowAny
from .models import User

# 카카오
KAKAO_API_KEY = getattr(settings, "KAKAO_API_KEY")
KAKAO_SECRET_CODE = getattr(settings, "KAKAO_SECRET_CODE")
# 구글
GOOGLE_API_KEY = getattr(settings, "GOOGLE_API_KEY")
# 네이버
NAVER_API_KEY = getattr(settings, "NAVER_API_KEY")
NAVER_SECRET_CODE = getattr(settings, "NAVER_SECRET_CODE")
# 깃허브
GITHUB_API_KEY = getattr(settings, "GITHUB_API_KEY")
GITHUB_SECRET_CODE = getattr(settings, "GITHUB_SECRET_CODE")
REDIRECT_URI = getattr(settings, "REDIRECT_URI")
# REDIRECT_URI = "http://127.0.0.1:5500/"
# print(GITHUB_API_KEY)
# print(GITHUB_SECRET_CODE)
print(REDIRECT_URI)


class UserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class mockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print("로그인된 유저")
        print(type(request.user.id))
        print(request.user.pk)
        return Response(
            {"로그인된 유저이름 /// " + f"{request.user.email}"}, status=status.HTTP_200_OK
        )


class UserListView(APIView):
    """
    admin관리자만 볼수있음
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """
    input: user의 pk
    output: email, username, profileimage

    추가구현필요기능-follow,following,bookmark,gpsmap
    연동필요-mycomment, myarticle, ??
    """

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        print("내 정보")
        user = request.user
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        print("내 정보 수정하기")
        print(request.user.username)
        user = request.user
        if user:
            return Response("내 프로필 정보 수정하기")


class SocialUrlView(APIView):
    def post(self, request):
        # print("소셜 인가코드 받기")
        social = request.data.get("social", None)
        if social is None:
            return Response(
                {"error": "소셜로그인이 아닙니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif social == "kakao-login":
            url = (
                "https://kauth.kakao.com/oauth/authorize?client_id="
                + KAKAO_API_KEY
                + "&redirect_uri="
                + REDIRECT_URI
                + "&response_type=code&prompt=login"
            )
            return Response({"url": url}, status=status.HTTP_200_OK)
        elif social == "naver-login":
            url = (
                "https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id="
                + NAVER_API_KEY
                + "&redirect_uri="
                + REDIRECT_URI
                + "&state=STATE_STRING"
            )
            return Response({"url": url}, status=status.HTTP_200_OK)
        elif social == "github-login":
            url = "https://github.com/login/oauth/authorize?client_id=" + GITHUB_API_KEY
            return Response({"url": url}, status=status.HTTP_200_OK)
        elif social == "google-login":
            return Response(
                {"key": GOOGLE_API_KEY, "redirecturi": REDIRECT_URI},
                status=status.HTTP_200_OK,
            )


class KakaoLoginView(APIView):
    def post(self, request):
        # print("소셜 인가코드 받아서 유저 데이터 저장")
        code = request.data.get("code", None)
        # print(code)
        token_url = f"https://kauth.kakao.com/oauth/token"
        redirect_uri = REDIRECT_URI

        if code is None:
            print("400error")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        access_token = requests.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_API_KEY,
                "redirect_uri": redirect_uri,
                "code": code,
                "client_secret": KAKAO_SECRET_CODE,
            },
            headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

        # access_token = response.json().get("access_token")
        access_token = access_token.json().get("access_token")
        user_data_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_datajson = user_data_request.json()
        user_data = user_datajson.get("kakao_account").get("profile")
        # print("user_data 딕셔너리 타입")
        print(user_data)
        email = user_datajson.get("kakao_account").get("email")
        username = user_data.get("nickname")
        profileimage = user_data.get("profile_image_url")
        # print(email)
        # print(username)
        # print(profileimage)
        try:
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["username"] = user.username
                refresh["login_type"] = user.login_type
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email,
                username=username,
                profileimage=profileimage,
                login_type="kakao",
            )
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["username"] = user.username
            refresh["login_type"] = user.login_type
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GoogleLoginView(APIView):
    def post(self, request):
        print("google소셜 인가코드 받아서 유저 데이터 저장")
        access_token = request.data["code"]
        # print(access_token)
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers
        )
        user_data = user_data_request.json()
        # print("user_data 딕셔너리 타입")
        print(user_data)

        email = user_data.get("email")
        username = user_data.get("name")
        profileimage = user_data.get("picture")
        # print(email)
        # print(username)
        # print(profileimage)
        try:
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["username"] = user.username
                refresh["login_type"] = user.login_type
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email,
                username=username,
                profileimage=profileimage,
                login_type="google",
            )
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["username"] = user.username
            refresh["login_type"] = user.login_type
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class NaverLoginView(APIView):
    def post(self, request):
        print("naver 소셜 인가코드 받아서 유저 데이터 저장")
        client_id = NAVER_API_KEY
        client_secret = NAVER_SECRET_CODE
        code = request.data.get("code")
        state = request.data.get("state")
        # print(code)
        # print(state)
        token_url = (
            f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code"
        )
        token_request = requests.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "state": state,
            },
        )
        access_token = token_request.json()
        access_token = token_request.json().get("access_token")
        user_data_request = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        user_datajson = user_data_request.json()
        user_data = user_datajson.get("response")
        # # print("user_data 딕셔너리 타입")
        print(user_data)
        email = user_data.get("email")
        username = user_data.get("nickname")
        profileimage = user_data.get("profile_image")
        # print(email)
        # print(username)
        # print(profileimage)
        try:
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["username"] = user.username
                refresh["login_type"] = user.login_type
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email,
                username=username,
                profileimage=profileimage,
                login_type="naver",
            )
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["username"] = user.username
            refresh["login_type"] = user.login_type
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GithubLoginView(APIView):
    def post(self, request):
        pass


class GithubLoginView(APIView):
    def post(self, request):
        print("github 소셜 인가코드 받아서 유저 데이터 저장")
        client_id = GITHUB_API_KEY
        client_secret = GITHUB_SECRET_CODE
        code = request.data.get("code")
        redirect_uri = REDIRECT_URI
        # print(code)
        # print(state)
        token_url = f"https://github.com/login/oauth/access_token"
        token_request = requests.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={
                "Accept": "application/json",
            },
        )
        access_token = token_request.json().get("access_token")
        user_data_request = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        user_datajson = user_data_request.json()
        print(user_datajson)
        user_url = "https://api.github.com/user"
        user_email_url = "https://api.github.com/user/emails"

        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_data = response.json()
        user_emails = response.json()

        user_email = None

        for email_data in user_emails:
            if email_data.get("primary") and email_data.get("verified"):
                user_email = email_data.get("email")

        email = user_data.get("email")
        username = user_data.get("nickname")
        profileimage = user_data.get("profile_image")
        print(email)
        print(username)
        print(profileimage)

        try:
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["username"] = user.username
                refresh["login_type"] = user.login_type
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email,
                username=username,
                profileimage=profileimage,
                login_type="github",
            )
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["username"] = user.username
            refresh["login_type"] = user.login_type
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
