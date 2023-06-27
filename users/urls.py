from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from users import views
from articles.views import UserArticleView, UserCommentView, BookMarkView
from emoticons.views import EmoticonView, EmoticonDetailView

urlpatterns = [
    path(
        "log-in/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("islogin/", views.isLoginUserView.as_view(), name="is_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("sign-up/", views.UserView.as_view(), name="signup"),
    # admin유저만
    path("userlist/", views.UserListView.as_view(), name="userlist"),
    # 로그인한 본인 프로필정보
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/article/", UserArticleView.as_view(), name="profile_article"
    ),  # 내가 작성한 게시글
    path(
        "profile/comment/", UserCommentView.as_view(), name="profile_comment"
    ),  # 내가 작성한 댓글
    path(
        "profile/bookmark/", BookMarkView.as_view(), name="profile_bookmark"
    ),  # 내가 북마크한 게시글
    path(
        "profile/emoticon/buy/", EmoticonView.as_view(), name="profile_buy_emoticon"
    ),  # 내가 구매한 이모티콘
    path(
        "profile/emoticon/apply/",
        EmoticonDetailView.as_view(),
        name="profile_apply_emoticon",
    ),  # 내가 신청한 이모티콘
    # 타인 유저 프로필
    path("<pk>/profile/", views.UserDetailView.as_view(), name="userprofile"),
    # 비밀번호 수정
    path(
        "password/change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    # 이메일 확인 후 user active
    path(
        "activate/<str:uidb64>/<str:token>",
        views.UserActivateView.as_view(),
        name="useractive",
    ),
    # 비밀번호 재설정(로그인X)
    path("password/reset/", views.ResetPasswordView.as_view(), name="reset_password"),
    path(
        "reset/<str:uidb64>/<str:token>",
        views.ResetPasswordEmailView.as_view(),
        name="reset_password_email",
    ),
    # 아이디 찾기
    path("find/id/", views.FindUserIDView.as_view(), name="find_userid"),
    # 회원가입 이메일 인증 재전송
    path("resend/email/", views.ResendEmailView.as_view(), name="resend_email"),
    # 소셜로그인
    path("social/", views.SocialUrlView.as_view(), name="social_login"),
    path("kakao-login/", views.KakaoLoginView.as_view(), name="kakao_login"),
    path("naver-login/", views.NaverLoginView.as_view(), name="naver_login"),
    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
    path("github-login/", views.GithubLoginView.as_view(), name="github_login"),
]
