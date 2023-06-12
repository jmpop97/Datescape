import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
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

a = getattr(settings, "KAKAO_API_KEY")
b = getattr(settings, "KAKAO_SECRET_CODE")


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

class SocialUrlView(APIView):
    def post(self,request):
        print("소셜 인가코드 받기")
        social = request.data.get('social',None)
        if social is None:
            return Response({'error':'소셜로그인이 아닙니다'},status=status.HTTP_400_BAD_REQUEST)
        elif social == 'kakao-login':
            url = 'https://kauth.kakao.com/oauth/authorize?client_id=' + a + '&redirect_uri=' + "http://127.0.0.1:5500/" + '&response_type=code&prompt=login'
            return Response({'url':url},status=status.HTTP_200_OK)
        # elif social == 'naver':
        #     url = 'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=' + config('NAVER_CLIENT_ID') + '&redirect_uri=' + config('REDIRECT_URI') + '&state=STATE_STRING'
        #     return Response({'url':url},status=status.HTTP_200_OK)   
        # elif social == 'google':
        #     return Response({'key':config('GOOGLE_API_KEY'),'redirecturi':config('REDIRECT_URI')},status=status.HTTP_200_OK)

class KakaoLoginView(APIView):
    def post(self, request):
        # print("소셜 인가코드 받아서 유저 데이터 저장")
        code = request.data.get("code", None)
        # print(code)
        token_url = f"https://kauth.kakao.com/oauth/token"
        redirect_uri = "http://127.0.0.1:5500/"

        if code is None:
            print("400error")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        access_token = requests.post(
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
        nickname = user_data.get("nickname")
        profileimage = user_data.get("profile_image_url")
        try:
            user = User.objects.get(email=email)
            if user.login_type == "normal":
                return Response(
                    {"error": "소셜로그인 가입이메일이아닙니다"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.username
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
                email=email, username=nickname, profileimage=profileimage, login_type="kakao"
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
        pass


class GoogleLoginView(APIView):
    def post(self, request):
        pass


class GithubLoginView(APIView):
    def post(self, request):
        pass
