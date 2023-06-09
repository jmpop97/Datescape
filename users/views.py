import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions

# from .tokens import account_activation_token
# from django.utils.http               import urlsafe_base64_encode,urlsafe_base64_decode
# from django.core.mail                import EmailMessage
# from django.utils.encoding           import force_bytes, force_text
# from django.http import HttpResponseRedirect
# from rest_framework.permissions import AllowAny
from .models import User

a = getattr(settings, "KAKAO_API_KEY")
b = getattr(settings, "KAKAO_SECRET_CODE")
print(a, b)


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
        print(request)
        return Response(
            {"로그인된 유저이름 /// " + f"{request.user}"}, status=status.HTTP_200_OK
        )


class KakaoLoginView(APIView):
    def get(self, request):
        app_key = a
        print(app_key, b)
        redirect_uri = "http://127.0.0.1:8000/users/kakao/login/callback"
        kakao_auth_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={app_key}&redirect_uri={redirect_uri}"
        )

    def post(self, request):
        code = request.data.get("code", None)
        token_url = f"https://kauth.kakao.com/oauth/token"
        redirect_uri = "http://127.0.0.1:8000/users/kakao/login/callback"

        if code is None:
            print("400error")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": a,
                "redirect_uri": redirect_uri,
                "code": code,
                "client_secret": b,
            },
            headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

        access_token = response.json().get("access_token")
        # access_token = access_token.json().get("access_token")
        user_data_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_datajson = user_data_request.json()
        user_data = user_datajson.get("kakao_account").get("profile")
        print(user_data)
        email = user_datajson.get("kakao_account").get("email")
        username = user_data.get("nickname")
        profileimage = user_data.get("profile_image_url")
        try:
            user = User.objects.get(email=email)
            if user.logintype == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = CustomTokenObtainPairSerializer.get_token(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.username
                refresh["logintype"] = user.logintype
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email, username=nickname, login_type="kakao"
            )
            user.set_unusable_password()
            user.save()
            profile = Profile.objects.get(user=user)
            profile.profileimage = profileimage
            profile.save()
            refresh = CustomTokenObtainPairSerializer.get_token(user)
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

    # def get(self, request):
    #     app_key = a
    #     print(app_key, b)
    #     redirect_uri = "http://127.0.0.1:8000/users/kakao/login/callback"
    #     kakao_api_url = "https://kauth.kakao.com/oauth/authorize"
    #     return redirect(
    #         f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={app_key}&redirect_uri={redirect_uri}"
    #     )

    # def post(self, request):
    #     print(a,b)
    #     code = request.data.get("code", None)
    #     token_url = f"https://kauth.kakao.com/oauth/token"
    #     redirect_uri = "http://127.0.0.1:8000/users/kakao/login/callback"

    #     if code is None:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    #     response = requests.post(
    #         token_url,
    #         data={
    #             "grant_type": "authorization_code",
    #             "client_id": a,
    #             "redirect_uri": redirect_uri,
    #             "code": code,
    #             "client_secret": b,
    #         },
    #         headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
    #     )

    #     access_token = response.json().get("access_token")
    #     user_url = "https://kapi.kakao.com/v2/user/me"
    #     response = requests.get(
    #         user_url,
    #         headers={
    #             "Authorization": f"Bearer {access_token}",
    #             "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    #         },
    #     )
    #     user_data = response.json()
    #     kakao_account = user_data.get("kakao_account")
    #     profile = kakao_account.get("profile")

    #     if not kakao_account.get("is_email_valid") and not kakao_account.get(
    #         "is_email_verified"
    #     ):
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    #     user_email = kakao_account.get("email")

    #     try:
    #         user = User.objects.get(email=user_email)
    #         refresh_token = CustomTokenObtainPairSerializer.get_token(user)

    #         return Response(
    #             {
    #                 "refresh": str(refresh_token),
    #                 "access": str(refresh_token.access_token),
    #             }
    #         )

    #     except User.DoesNotExist:
    #         user = User.objects.create_user(email=user_email)
    #         user.set_unusable_password()
    #         user.username = profile.get("username", f"user#{user.pk}")
    #         user.save()

    #         refresh_token = CustomTokenObtainPairSerializer.get_token(user)

    #         return Response(
    #             {
    #                 "refresh": str(refresh_token),
    #                 "access": str(refresh_token.access_token),
    #             }
    #         )


class NaverLoginView(APIView):
    def post(self, request):
        pass


class GoogleLoginView(APIView):
    def post(self, request):
        pass


class GithubLoginView(APIView):
    def post(self, request):
        pass
