from django.urls import path
from articles import views


urlpatterns = [
    path("", views.NaverMapView.as_view(), name="search_map"),

    path("location-list/", views.LocationListView.as_view(), name="location_list"),
    path(
        "location-articles/",
        views.LocationArticlesView.as_view(),
        name="location_articles",
    ),
    path("article-search/", views.ArticleSearchView.as_view(), name="article_search"),
    path(
        "<int:article_id>/comments/", views.CommentView.as_view(), name="comment_view"
    ),  # 댓글 생성 / 조회 / 수정 / 삭제
    path(
        "comments/like/", views.CommentLikeView.as_view(), name="comment_like_view"
    ),  # 댓글 좋아요
]
