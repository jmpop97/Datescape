from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users import views

urlpatterns = [
    path("log-in/", views.CustomTokenObtainPairView.as_view(),
         name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("sign-up/", views.UserView.as_view(), name="signup"),
    path("mock/", views.mockView.as_view()),
    # path('/activate/<str:uidb64>/<str:token>', views.Activate.as_view()),
    path("social/", views.SocialUrlView.as_view(), name='social_login'),
    path("kakao-login/", views.KakaoLoginView.as_view()),
    # path("naver-login/", views.NaverLoginView.as_view()),
    # path("google-login/", views.GoogleLoginView.as_view()),
    # path("github-login/", views.GithubLoginView.as_view()),
]
