from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users import views

urlpatterns = [
    path(
        "log-in/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("sign-up/", views.UserView.as_view(), name="signup"),
    # admin유저만
    path("userlist/", views.UserListView.as_view(), name="userlist"),
    # 로그인한 본인 프로필정보
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # 타인 유저 프로필
    path("<pk>/profile/", views.UserDetailView.as_view(), name="userprofile"),
    # 비밀번호 수정
    path("password/change/", views.PasswordChangeView.as_view(), name="userprofile"),
    # path('/activate/<str:uidb64>/<str:token>', views.Activate.as_view()),
    path("social/", views.SocialUrlView.as_view(), name="social_login"),
    path("kakao-login/", views.KakaoLoginView.as_view(), name="kakao_login"),
    path("naver-login/", views.NaverLoginView.as_view(), name="naver_login"),
    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
    path("github-login/", views.GithubLoginView.as_view(), name="github_login"),
]
