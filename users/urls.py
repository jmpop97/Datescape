from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users import views

urlpatterns = [
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", views.UserView.as_view(), name="signup"),
    path("mock/", views.mockView.as_view()),
    # path('/activate/<str:uidb64>/<str:token>', views.Activate.as_view()),
    path("kakao-login/", views.KakaoLoginView.as_view()),
    # path("naver-login/", views.NaverLoginView.as_view()),
    # path("google-login/", views.GoogleLoginView.as_view()),
    # path("github-login/", views.GithubLoginView.as_view()),
    # 구글 소셜로그인
    # path('google/login', views.google_login, name='google_login'),
    # path('google/callback/', views.google_callback, name='google_callback'),
    # path('google/login/finish/', views.GoogleLogin.as_view(), name='google_login_todjango'),
]
