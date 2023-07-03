import requests, random, string
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserDetailSerializer,
    ProfileEditSerializer,
    PasswordEditSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions

from users.tokens import account_activation_token
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
EMAIL_HOST_PASSWORD = getattr(settings, "EMAIL_HOST_PASSWORD")
BACK_URL = getattr(settings, "BACK_URL")
DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL")


# loadbalancer 로그 지우기
def home(request):
    return HttpResponse("")


# 아이디 찾기
class FindUserIDView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                # serializer = UserSerializer(user)
                # return Response(serializer.data, status=status.HTTP_200_OK)
                return Response((user.username), status=status.HTTP_200_OK)
            else:
                return Response(("소셜로그인을 이용해주세요"), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"해당 이메일에 일치하는 회원이 없습니다!"}, status=status.HTTP_400_BAD_REQUEST
            )


# 비밀번호 재설정 이메일보내기
class ResetPasswordEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                return redirect(
                    f"{REDIRECT_URI}templates/reset_password_change.html?uid={uid}"
                )

            return HttpResponse("만료된 링크입니다", status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return JsonResponse({"message": "INVALID_KEY"}, status=400)


# 회원가입 후 이메일 인증 확인 view
class UserActivateView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        try:
            if user is not None and account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect(REDIRECT_URI)
            else:
                return HttpResponse("만료된 링크입니다", status=status.HTTP_400_BAD_REQUEST)

        except ValidationError:
            return JsonResponse({"message": "TYPE_ERROR"}, status=400)

        except KeyError:
            return JsonResponse({"message": "INVALID_KEY"}, status=400)


# 회원가입
class UserView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            type = user.login_type
            if type != "normal":
                return Response(
                    f"이미 가입된 회원입니다. {type}로 가입하셨습니다. 확인해주세요.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                "이미 가입된 이메일입니다. 다른 이메일을 사용해주세요.", status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                "이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "회원가입완료, 이메일을 확인해주세요!!"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


# 로그인
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 로그인된 유저 확인하기
class isLoginUserView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            user = request.user

            if user:
                serializer = UserSerializer(user)

                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"message": f"${serializer.errors}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except:
            return Response(
                {f"{user}", "로그인되지 않았습니다. 다시 로그인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # return Response(
        #     {"message": f"${serializer.errors}"}, status=status.HTTP_401_UNAUTHORIZED
        # )
        return Response({"로그인되지 않았습니다. 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)


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

    추가구현필요기능-follow,following
    """

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 마이페이지-내정보
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        user = request.user

        nickname = request.data.get("nickname")

        if User.objects.filter(nickname=nickname).exists():
            return Response(
                "이미 사용 중인 닉네임입니다. 다른 닉네임을 사용해주세요.", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProfileEditSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()

            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["username"] = user.username
            refresh["login_type"] = user.login_type
            return Response(
                (serializer.data, str(refresh), str(refresh.access_token)),
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request):
        user = request.user
        if user:
            user.is_active = False
            user.user_status = "spleep"
            user.save()
            return Response({f"{user} 휴면중"}, status=status.HTTP_200_OK)
        return Response({"잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 재설정 이메일에서 링크 보내기
class ResetPasswordView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get("email")
            user = User.objects.get(email=user_email)
            if user:
                if user.login_type == "normal":
                    html = render_to_string(
                        "password_reset.html",
                        {
                            "backend_base_url": BACK_URL,
                            "uidb64": urlsafe_base64_encode(force_bytes(user.id))
                            .encode()
                            .decode(),
                            "token": account_activation_token.make_token(user),
                        },
                    )
                    to_email = user.email
                    send_mail(
                        "DateScape : 비밀번호 초기화 인증 메일입니다!",
                        "_",
                        DEFAULT_FROM_EMAIL,
                        [to_email],
                        html_message=html,
                    )
                    return Response(("비밀번호 재설정 이메일 전송!"), status=status.HTTP_200_OK)
                else:
                    return Response(
                        ("소셜로그인 회원입니다."), status=status.HTTP_400_BAD_REQUEST
                    )

        except User.DoesNotExist:
            return Response(
                {"error": "해당 이메일에 일치하는 회원이 없습니다!"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        new_password1 = request.data.get("new_password1")
        new_password2 = request.data.get("new_password2")
        user_id = request.data.get("user_id")

        user = User.objects.get(id=user_id)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                "해당 이메일에 일치하는 회원이 없습니다!", status=status.HTTP_400_BAD_REQUEST
            )

        if not new_password1 or not new_password2:
            return Response("비밀번호는 필수입니다!", status=status.HTTP_400_BAD_REQUEST)
        if new_password1 != new_password2:
            return Response(
                "비밀번호가 일치하지 않습니다. 다시 확인해주세요!", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PasswordEditSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "비밀번호 재설정이 완료되었습니다!"})
        else:
            return Response(
                {"message": f"${serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 일반회원 유저만 로그인중일때 비번 변경
class PasswordChangeView(APIView):
    """
    {
        "new_password1":"new_password",
        "new_password2":"new_password"
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.login_type == "normal":
            serializer = PasswordEditSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(("비밀번호 변경하기 성공"), status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                ("SNS계정에서 변경하실 수 있습니다."), status=status.HTTP_400_BAD_REQUEST
            )


# 회원가입 이메일 인증 재전송
class ResendEmailView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get("email")
            user = User.objects.get(email=user_email)
            if user:
                if user.login_type == "normal":
                    html = render_to_string(
                        "register_email.html",
                        {
                            "backend_base_url": BACK_URL,
                            "uidb64": urlsafe_base64_encode(force_bytes(user.id))
                            .encode()
                            .decode(),
                            "token": account_activation_token.make_token(user),
                        },
                    )
                    to_email = user.email
                    send_mail(
                        "DateScape : 회원가입 인증 재전송 이메일입니다. 확인해주세요.",
                        "_",
                        DEFAULT_FROM_EMAIL,
                        [to_email],
                        html_message=html,
                    )
                    return Response(("일반회원 이메일 인증 재전송 성공!"), status=status.HTTP_200_OK)
                else:
                    return Response(
                        ("소셜로그인 회원입니다."), status=status.HTTP_400_BAD_REQUEST
                    )

        except User.DoesNotExist:
            return Response(
                {"error": "해당 이메일에 일치하는 회원이 없습니다!"}, status=status.HTTP_400_BAD_REQUEST
            )


class SocialUrlView(APIView):
    def post(self, request):
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
        code = request.data.get("code", None)
        token_url = f"https://kauth.kakao.com/oauth/token"
        redirect_uri = REDIRECT_URI

        if code is None:
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
        email = user_datajson.get("kakao_account").get("email")
        nickname = user_data.get("nickname")
        image = user_data.get("thumbnail_image_url", None)

        ran_str = ""
        ran_num = random.randint(0, 99999)
        for i in range(10):
            ran_str += str(random.choice(string.ascii_letters + str(ran_num)))

        username = "kakao_" + ran_str
        try:
            user = User.objects.get(email=email)
            type = user.login_type
            if user.login_type == "normal":
                return Response(
                    "일반회원으로 이미 가입하셨습니다. 아이디, 비번을 잊으셨다면 아이디 찾기, 비밀번호 재설정을 이용하세요.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            elif type != "kakao":
                return Response(
                    f"{user}님의 상태는 휴면중입니다.", status=status.HTTP_400_BAD_REQUEST
                )
            elif user.is_active == False:
                return Response(
                    f"{user}님의 상태는 휴면중입니다.", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.nickname
                refresh["login_type"] = user.login_type
                user.last_login = timezone.now()
                user.save()
                refresh["last_login"] = str(user.last_login)
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
                nickname=nickname,
                profileimage=None,
                profileimageurl=image,
                login_type="kakao",
            )
            user.last_login = timezone.now()
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["login_type"] = user.login_type
            refresh["last_login"] = str(user.last_login)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data["code"]
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers
        )
        user_data = user_data_request.json()

        email = user_data.get("email")
        nickname = user_data.get("name")
        image = user_data.get("picture", None)

        ran_str = ""
        ran_num = random.randint(0, 99999)
        for i in range(10):
            ran_str += str(random.choice(string.ascii_letters + str(ran_num)))

        username = "google_" + ran_str
        try:
            user = User.objects.get(email=email)
            type = user.login_type

            if type == "normal":
                return Response(
                    "일반회원으로 이미 가입하셨습니다. 아이디, 비번을 잊으셨다면 아이디 찾기, 비밀번호 재설정을 이용하세요.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            elif type != "google":
                return Response(
                    f"{type}으로 가입하셨습니다. 다시 로그인해주세요.", status=status.HTTP_400_BAD_REQUEST
                )

            elif user.is_active == False:
                return Response(
                    f"{user}님의 상태는 휴면중입니다.", status=status.HTTP_400_BAD_REQUEST
                )

            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.nickname
                refresh["login_type"] = user.login_type
                user.last_login = timezone.now()
                user.save()
                refresh["last_login"] = str(user.last_login)
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
                nickname=nickname,
                login_type="google",
                profileimage=None,
                profileimageurl=image,
            )
            user.last_login = timezone.now()
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["login_type"] = user.login_type
            refresh["last_login"] = str(user.last_login)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class NaverLoginView(APIView):
    def post(self, request):
        client_id = NAVER_API_KEY
        client_secret = NAVER_SECRET_CODE
        code = request.data.get("code")
        state = request.data.get("state")
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
        email = user_data.get("email")
        nickname = user_data.get("nickname")
        image = user_data.get("profile_image")

        ran_str = ""
        ran_num = random.randint(0, 99999)
        for i in range(10):
            ran_str += str(random.choice(string.ascii_letters + str(ran_num)))

        username = "naver_" + ran_str
        try:
            user = User.objects.get(email=email)
            type = user.login_type

            if type == "normal":
                return Response(
                    "일반회원으로 이미 가입하셨습니다. 아이디, 비번을 잊으셨다면 아이디 찾기, 비밀번호 재설정을 이용하세요.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif type != "naver":
                return Response(
                    f"{type}으로 가입하셨습니다. 확인해 주세요.", status=status.HTTP_400_BAD_REQUEST
                )
            elif user.is_active == False:
                return Response(
                    f"{user}님의 상태는 휴면중입니다.", status=status.HTTP_400_BAD_REQUEST
                )

            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.nickname
                refresh["login_type"] = user.login_type
                user.last_login = timezone.now()
                user.save()
                refresh["last_login"] = str(user.last_login)
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
                nickname=nickname,
                username=username,
                profileimage=None,
                profileimageurl=image,
                login_type="naver",
            )
            user.last_login = timezone.now()
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["login_type"] = user.login_type
            refresh["last_login"] = str(user.last_login)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GithubLoginView(APIView):
    def post(self, request):
        client_id = GITHUB_API_KEY
        client_secret = GITHUB_SECRET_CODE
        code = request.data.get("code")
        redirect_uri = REDIRECT_URI
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
        # user_data_request = requests.get(
        #     "https://api.github.com/user",
        #     headers={
        #         "Authorization": f"Bearer {access_token}",
        #     },
        # )
        # user_datajson = user_data_request.json()
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

        response = requests.get(
            user_email_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_emails = response.json()

        user_email = None

        for email_data in user_emails:
            if email_data.get("primary") and email_data.get("verified"):
                user_email = email_data.get("email")

        email = user_email
        nickname = user_data.get("name")
        image = user_data.get("avatar_url")

        ran_str = ""
        ran_num = random.randint(0, 99999)
        for i in range(10):
            ran_str += str(random.choice(string.ascii_letters + str(ran_num)))

        username = "github_" + ran_str
        # user.profileimage = None
        try:
            user = User.objects.get(email=email)
            type = user.login_type
            if type == "normal":
                return Response(
                    "일반회원으로 이미 가입하셨습니다. 아이디, 비번을 잊으셨다면 아이디 찾기, 비밀번호 재설정을 이용하세요.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif type != "github":
                return Response(
                    f"{type}으로 가입하셨습니다. 확인해 주세요.", status=status.HTTP_400_BAD_REQUEST
                )
            elif user.is_active == False:
                return Response(
                    f"{user}님의 상태는 휴면중입니다.", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.nickname
                refresh["login_type"] = user.login_type
                user.last_login = timezone.now()
                user.save()
                refresh["last_login"] = str(user.last_login)
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
                nickname=nickname,
                profileimage=None,
                profileimageurl=image,
                login_type="github",
            )
            user.last_login = timezone.now()
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["login_type"] = user.login_type
            refresh["last_login"] = str(user.last_login)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
