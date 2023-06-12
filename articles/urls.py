from django.urls import path
from articles import views


urlpatterns = [
    path("", views.ArticleView.as_view(), name="article_list"),
    path("location-list/", views.LocationListView.as_view(), name="location_list"),
    path(
        "location-articles/",
        views.LocationArticlesView.as_view(),
        name="location_articles",
    ),
    path("<int:article_id>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("coordinate/", views.KakaoMapCoordinateView.as_view(), name="coordinate_map"),
    path("article-search/", views.ArticleSearchView.as_view(), name="article_search"),
    path("search/", views.KakaoMapSearchView.as_view(), name="search_map"),
    path("map-save", views.KakaoSaveView.as_view(), name="save_map"),
    path(
        "<int:article_id>/comments/", views.CommentView.as_view(), name="comment_view"
    ),  # 댓글 생성 / 조회 / 수정 / 삭제
    path(
        "comments/like/", views.CommentLikeView.as_view(), name="comment_like_view"
    ),  # 댓글 좋아요
]
