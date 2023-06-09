from django.urls import path
from emoticons import views


urlpatterns = [
    path(
        "", views.EmoticonView.as_view(), name="emoticon"
    ),  # 구매한 이모티콘 조회 / 제작 신청 / 수정 / 삭제
    path("list/", views.EmoticonListView.as_view(), name="emoticon_list"),  # 전체 이모티콘 조회
    path(
        "<int:emoticon_id>/", views.EmoticonDetailView.as_view(), name="emoticon_detail"
    ),  # 이모티콘 자세히 보기
    path(
        "temp/", views.EmoticonTempListView.as_view(), name="emoticon_temp_list"
    ),  # 임시저장 이모티콘 리스트
    path(
        "payment/", views.UserEmoticonListView.as_view(), name="user_buy_emoticon"
    ),  # 이모티콘 결제 DB저장
    path(
        "images/", views.EmoticonImageView.as_view(), name="emoticon_image"
    ),  # 이모티콘 이미지 전부 다 가져오기
]
